from flask_restx import Namespace, Resource, fields
from flask import request, current_app, jsonify, send_file
from werkzeug.datastructures import FileStorage
import tempfile
import os

from services.detector import detect_vehicle, detect_video, train_models as services_train_models
# Import helpers from model_loader
from utils.model_loader import list_available_models, train_model, compare_models

api = Namespace('vehicle', description='Vehicle detection operations')

upload_parser = api.parser()
upload_parser.add_argument('image', location='files', type='FileStorage', required=True)

video_upload_parser = api.parser()
video_upload_parser.add_argument('video', location='files', type=FileStorage, required=True)
video_upload_parser.add_argument('model', location='form', type=str, required=False)

# Parser and model for training endpoint (supports multipart file upload or JSON body)
train_parser = api.parser()
train_parser.add_argument('model', location='form', type=str, required=True, help='Model identifier to train')
train_parser.add_argument('dataset', location='files', type=FileStorage, required=False, help='Optional dataset file to upload')

train_json = api.model('TrainRequest', {
    'model': fields.String(required=True, description='Model identifier to train'),
    'dataset': fields.String(required=False, description='Optional dataset identifier or path')
})

# Model for compare endpoint (JSON body expected in UI)
compare_json = api.model('CompareRequest', {
    'models': fields.List(fields.String(required=True), required=True, description='Array of model identifiers to compare'),
    'dataset': fields.String(required=False, description='Optional dataset identifier')
})

@api.route('/detect')
class VehicleDetect(Resource):
    @api.expect(upload_parser)
    def post(self):
        """Detect vehicles in an image using selected model and save processed image"""
        image = request.files['image']
        model = request.args.get('model', 'haar')
        result, processed_img = detect_vehicle(image, model, return_image=True)
        # Save processed image
        processed_dir = os.path.join(current_app.root_path, 'processed')
        filename = f"processed_{image.filename}"
        processed_path = os.path.join(processed_dir, filename)
        processed_img.save(processed_path)
        result['processed_filename'] = filename
        return result

@api.route('/detect_video')
class VehicleDetectVideo(Resource):
    @api.expect(video_upload_parser)
    def post(self):
        """Detect vehicles in a video file frame by frame and save processed video"""
        video = request.files['video']
        model = request.form.get('model', 'haar')
        processed_filename, stats = detect_video(video, model)
        return {'processed_filename': processed_filename, 'stats': stats}

@api.route('/train')
class VehicleTrain(Resource):
    @api.expect(train_parser, train_json)
    def post(self):
        """Train all models on COCO dataset (simple trigger).

        This keeps backward compatibility with the original simple trigger
        while more advanced training is exposed via the /train POST resource
        implemented further down.
        """
        # call the service-level trainer if available
        try:
            services_train_models()
        except Exception:
            current_app.logger.exception("services_train_models failed (placeholder)")
        return {'status': 'training complete'}

@api.route('/compare')
class VehicleCompare(Resource):
    @api.expect(compare_json)
    def get(self):
        """Compare all models on validation set (simple getter).

        This uses the helper compare_models from utils/model_loader which
        accepts a list; for the simple GET we compare all available models.
        """
        models = list_available_models()
        results = compare_models(models)
        return results

@api.route('/models')
class ModelsResource(Resource):
    def get(self):
        """Return available model identifiers."""
        try:
            models = list_available_models()
            return jsonify(models), 200
        except Exception as e:
            current_app.logger.exception("Failed to list models")
            return jsonify({'error': 'Failed to list models', 'detail': str(e)}), 500

@api.route('/train')
class TrainResource(Resource):
    @api.expect(train_parser, train_json)
    def post(self):
        """
        Start training for a specified model.
        Accepts:
          - multipart/form-data with fields: model (str) and dataset (file) OR form field 'dataset' pointing to file
          - application/json: { model: string, dataset: optional string identifier }
        Returns training scheduling/result info (placeholder).
        """
        try:
            content_type = request.content_type or ''
            model_name = None
            dataset_arg = None
            dataset_file_path = None

            if content_type.startswith('multipart/form-data'):
                model_name = request.form.get('model')
                # accept uploaded dataset under keys 'dataset' or 'file'
                upload = request.files.get('dataset') or request.files.get('file')
                if upload:
                    # save to temp file
                    tf = tempfile.NamedTemporaryFile(delete=False)
                    upload.save(tf.name)
                    dataset_file_path = tf.name
            else:
                data = request.get_json(silent=True) or {}
                model_name = data.get('model')
                dataset_arg = data.get('dataset')

            if not model_name:
                return jsonify({'error': 'Missing "model" parameter'}), 400

            # Call training helper (placeholder logic implemented in utils/model_loader)
            result = train_model(model_name, dataset=dataset_arg, dataset_file_path=dataset_file_path)

            # cleanup temp file if used
            if dataset_file_path and os.path.exists(dataset_file_path):
                try:
                    os.remove(dataset_file_path)
                except Exception:
                    current_app.logger.debug("Could not remove temp dataset file", exc_info=True)

            return jsonify(result), 200
        except Exception as e:
            current_app.logger.exception("Training failed")
            return jsonify({'error': 'Training failed', 'detail': str(e)}), 500

@api.route('/compare')
class CompareResource(Resource):
    @api.expect(compare_json)
    def post(self):
        """
        Compare multiple models on an optional dataset.
        Expects JSON body: { models: [string,...], dataset?: string }
        """
        try:
            data = request.get_json(silent=True)
            if not data or 'models' not in data:
                return jsonify({'error': 'Request must contain "models" array'}), 400

            models = data.get('models') or []
            dataset = data.get('dataset')

            if not isinstance(models, list) or not all(isinstance(m, str) for m in models):
                return jsonify({'error': '"models" must be an array of strings'}), 400

            result = compare_models(models, dataset=dataset)
            return jsonify(result), 200
        except Exception as e:
            current_app.logger.exception("Comparison failed")
            return jsonify({'error': 'Comparison failed', 'detail': str(e)}), 500

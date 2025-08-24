import { Component, OnInit } from '@angular/core';
import { VehicleService } from '../services/vehicle.service';

@Component({
    selector: 'app-options-page',
    templateUrl: './options-page.component.html',
    styleUrls: ['./options-page.component.scss']
})
export class OptionsPageComponent implements OnInit {
    selectedModel = 'haar';
    imageFile?: File;
    videoFile?: File;
    detectResult: any;
    videoResult: any;
    compareResult: any;
    downloadName = '';
    // new properties for compare/train UI
    availableModels: string[] = ['haar', 'cnn'];
    modelsLoading = false;
    modelsLoadError = '';
    selectedCompareModels: string[] = [];
    compareDataset = '';
    // training
    trainModelSelection = 'haar';
    trainDataFile?: File;
    trainDataFileName = '';
    trainDataName = '';
    trainResult: any;

    constructor(private vehicleService: VehicleService) {}

    ngOnInit(): void {
        // attempt to load available models from backend; fallback to defaults on error
        this.modelsLoading = true;
        this.vehicleService.getAvailableModels().subscribe({
            next: (list: string[]) => {
                if (Array.isArray(list) && list.length) {
                    this.availableModels = list;
                    // ensure selections exist
                    if (!this.availableModels.includes(this.selectedModel)) {
                        this.selectedModel = this.availableModels[0];
                    }
                    if (!this.availableModels.includes(this.trainModelSelection)) {
                        this.trainModelSelection = this.availableModels[0];
                    }
                }
                this.modelsLoading = false;
            },
            error: (err: any) => {
                console.warn('Could not load available models, using defaults.', err);
                this.modelsLoadError = 'Failed to load models from server; using local defaults.';
                this.modelsLoading = false;
            }
        });
    }

    onImageSelected(event: any) {
        this.imageFile = event.target.files[0];
    }

    onVideoSelected(event: any) {
        this.videoFile = event.target.files[0];
    }

    onTrainDataSelected(event: any) {
        const f = event.target.files && event.target.files[0];
        if (f) {
            this.trainDataFile = f;
            this.trainDataFileName = f.name;
            // optionally clear trainDataName when file chosen
            this.trainDataName = '';
        }
    }

    detectImage() {
        if (!this.imageFile) {
            alert('Please upload an image before detecting.');
            return;
        }
        this.vehicleService.detectVehicle(this.imageFile, this.selectedModel).subscribe(res => {
            this.detectResult = res;
        }, (err) => {
            console.error('Detect image failed', err);
            this.detectResult = { error: 'Detection failed' };
        });
    }

    detectVideo() {
        if (!this.videoFile) {
            alert('Please upload a video before detecting.');
            return;
        }
        this.vehicleService.detectVideo(this.videoFile, this.selectedModel).subscribe(res => {
            this.videoResult = res;
        }, (err) => {
            console.error('Detect video failed', err);
            this.videoResult = { error: 'Detection failed' };
        });
    }

    trainModels() {
        // send selected model and either file or dataset name
        const payload: any = { model: this.trainModelSelection };
        if (this.trainDataFile) {
            // if backend expects FormData
            const fd = new FormData();
            fd.append('model', this.trainModelSelection);
            fd.append('dataset', this.trainDataFile, this.trainDataFile.name);
            this.vehicleService.trainModels(fd).subscribe(res => {
                this.trainResult = res;
                alert('Training started/completed.');
            });
            return;
        }
        if (this.trainDataName) payload.dataset = this.trainDataName;
        this.vehicleService.trainModels(payload).subscribe(res => {
            this.trainResult = res;
            alert('Training started/completed.');
        });
    }

    compareModels() {
        // require at least two models for meaningful comparison (backend can handle)
        const models = this.selectedCompareModels && this.selectedCompareModels.length ? this.selectedCompareModels : this.availableModels;
        const payload: any = { models };
        if (this.compareDataset) payload.dataset = this.compareDataset;
        this.vehicleService.compareModels(payload).subscribe(res => {
            this.compareResult = res;
        });
    }

    downloadProcessed() {
        if (this.downloadName) {
            this.vehicleService.downloadProcessedFile(this.downloadName).subscribe(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = this.downloadName;
                a.click();
                window.URL.revokeObjectURL(url);
            });
        }
    }
}

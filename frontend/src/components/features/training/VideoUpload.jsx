import React, { useState, useRef } from 'react';
import Button from '../../common/Button';
import trainingService from '../../../services/trainingService';

const VideoUpload = ({ onUploadComplete, onCancel, existingStyles = [] }) => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [metadata, setMetadata] = useState({
        title: '',
        description: '',
        technique_name: '',
        style: '',
        is_private: true,
        tags: ''
    });
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    const [error, setError] = useState('');
    const [validationErrors, setValidationErrors] = useState({});

    const fileInputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    };

    const handleFileSelect = (file) => {
        setError('');
        setValidationErrors({});

        // Validate file
        const validation = trainingService.validateVideoFile(file);
        if (!validation.isValid) {
            setError(validation.errors.join(' '));
            return;
        }

        setSelectedFile(file);

        // Auto-populate title if empty
        if (!metadata.title) {
            const nameWithoutExtension = file.name.replace(/\.[^/.]+$/, '');
            setMetadata(prev => ({
                ...prev,
                title: nameWithoutExtension
            }));
        }
    };

    const handleFileInputChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFileSelect(e.target.files[0]);
        }
    };

    const handleMetadataChange = (field, value) => {
        setMetadata(prev => ({
            ...prev,
            [field]: value
        }));

        // Clear validation error for this field
        if (validationErrors[field]) {
            setValidationErrors(prev => ({
                ...prev,
                [field]: undefined
            }));
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setError('Please select a video file');
            return;
        }

        // Validate metadata
        const validation = trainingService.validateVideoMetadata(metadata);
        if (!validation.isValid) {
            setValidationErrors(validation.errors);
            return;
        }

        setIsUploading(true);
        setError('');
        setUploadProgress(0);

        try {
            const result = await trainingService.uploadVideo(
                selectedFile,
                metadata,
                (progress) => setUploadProgress(progress)
            );

            console.log('✅ Video uploaded successfully:', result);

            if (onUploadComplete) {
                onUploadComplete(result.video);
            }
        } catch (error) {
            console.error('❌ Video upload failed:', error);
            setError(
                error.response?.data?.message ||
                'Failed to upload video. Please try again.'
            );
        } finally {
            setIsUploading(false);
            setUploadProgress(0);
        }
    };

    const handleCancel = () => {
        setSelectedFile(null);
        setMetadata({
            title: '',
            description: '',
            technique_name: '',
            style: '',
            is_private: true,
            tags: ''
        });
        setError('');
        setValidationErrors({});
        setUploadProgress(0);

        if (onCancel) {
            onCancel();
        }
    };

    const removeFile = () => {
        setSelectedFile(null);
        setError('');
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <div className="video-upload-container">
            <div className="upload-header">
                <h3>Upload Training Video</h3>
                <p>Upload a video of your technique for AI analysis and progress tracking</p>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                    <button onClick={() => setError('')} className="error-close">×</button>
                </div>
            )}

            {/* File Upload Area */}
            <div
                className={`file-upload-area ${dragActive ? 'drag-active' : ''} ${selectedFile ? 'has-file' : ''}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => !selectedFile && fileInputRef.current?.click()}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="video/*"
                    onChange={handleFileInputChange}
                    style={{ display: 'none' }}
                />

                {selectedFile ? (
                    <div className="file-selected">
                        <div className="file-info">
                            <div className="file-icon">🎥</div>
                            <div className="file-details">
                                <div className="file-name">{selectedFile.name}</div>
                                <div className="file-meta">
                                    {trainingService.formatFileSize(selectedFile.size)}
                                    {selectedFile.type && ` • ${selectedFile.type}`}
                                </div>
                            </div>
                        </div>
                        <button
                            type="button"
                            onClick={(e) => {
                                e.stopPropagation();
                                removeFile();
                            }}
                            className="remove-file-btn"
                        >
                            ×
                        </button>
                    </div>
                ) : (
                    <div className="upload-prompt">
                        <div className="upload-icon">📁</div>
                        <h4>Drag & drop your video here</h4>
                        <p>or click to browse files</p>
                        <div className="supported-formats">
                            Supported: MP4, MOV, AVI, MKV, WMV, WebM (Max 500MB)
                        </div>
                    </div>
                )}
            </div>

            {/* Upload Progress */}
            {isUploading && (
                <div className="upload-progress">
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${uploadProgress}%` }}
                        ></div>
                    </div>
                    <div className="progress-text">{uploadProgress}% uploaded</div>
                </div>
            )}

            {/* Metadata Form */}
            <div className="metadata-form">
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="video-title">Title *</label>
                        <input
                            id="video-title"
                            type="text"
                            className={`form-input ${validationErrors.title ? 'error' : ''}`}
                            value={metadata.title}
                            onChange={(e) => handleMetadataChange('title', e.target.value)}
                            placeholder="Enter video title"
                            maxLength={200}
                        />
                        {validationErrors.title && (
                            <div className="field-error">{validationErrors.title}</div>
                        )}
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group half-width">
                        <label htmlFor="technique-name">Technique</label>
                        <input
                            id="technique-name"
                            type="text"
                            className={`form-input ${validationErrors.technique_name ? 'error' : ''}`}
                            value={metadata.technique_name}
                            onChange={(e) => handleMetadataChange('technique_name', e.target.value)}
                            placeholder="e.g., Roundhouse Kick"
                            maxLength={100}
                        />
                        {validationErrors.technique_name && (
                            <div className="field-error">{validationErrors.technique_name}</div>
                        )}
                    </div>

                    <div className="form-group half-width">
                        <label htmlFor="style">Martial Art Style</label>
                        <input
                            id="style"
                            type="text"
                            list="styles-list"
                            className={`form-input ${validationErrors.style ? 'error' : ''}`}
                            value={metadata.style}
                            onChange={(e) => handleMetadataChange('style', e.target.value)}
                            placeholder="e.g., Taekwondo"
                            maxLength={50}
                        />
                        <datalist id="styles-list">
                            {existingStyles.map(style => (
                                <option key={style} value={style} />
                            ))}
                        </datalist>
                        {validationErrors.style && (
                            <div className="field-error">{validationErrors.style}</div>
                        )}
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="description">Description</label>
                        <textarea
                            id="description"
                            className={`form-textarea ${validationErrors.description ? 'error' : ''}`}
                            value={metadata.description}
                            onChange={(e) => handleMetadataChange('description', e.target.value)}
                            placeholder="Describe what you're working on, areas of focus, or any specific feedback you'd like..."
                            rows={3}
                            maxLength={1000}
                        />
                        {validationErrors.description && (
                            <div className="field-error">{validationErrors.description}</div>
                        )}
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group half-width">
                        <label htmlFor="tags">Tags (comma-separated)</label>
                        <input
                            id="tags"
                            type="text"
                            className="form-input"
                            value={metadata.tags}
                            onChange={(e) => handleMetadataChange('tags', e.target.value)}
                            placeholder="e.g., competition prep, sparring, forms"
                        />
                    </div>

                    <div className="form-group half-width">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={metadata.is_private}
                                onChange={(e) => handleMetadataChange('is_private', e.target.checked)}
                            />
                            <span className="checkbox-text">Keep video private</span>
                        </label>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="form-actions">
                <Button
                    variant="secondary"
                    onClick={handleCancel}
                    disabled={isUploading}
                >
                    Cancel
                </Button>
                <Button
                    variant="primary"
                    onClick={handleUpload}
                    disabled={!selectedFile || isUploading}
                    loading={isUploading}
                >
                    {isUploading ? 'Uploading...' : 'Upload Video'}
                </Button>
            </div>
        </div>
    );
};

export default VideoUpload;
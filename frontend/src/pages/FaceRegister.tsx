import { useRef, useState } from 'react';
import { api } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { Camera } from 'lucide-react';

export default function FaceRegister() {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [isStreaming, setIsStreaming] = useState(false);
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                setIsStreaming(true);
            }
        } catch (err) {
            setMessage('Error accessing camera');
        }
    };

    const captureAndRegister = async () => {
        if (!videoRef.current || !canvasRef.current) return;

        const context = canvasRef.current.getContext('2d');
        if (!context) return;

        context.drawImage(videoRef.current, 0, 0, 640, 480);

        canvasRef.current.toBlob(async (blob) => {
            if (!blob) return;

            const formData = new FormData();
            formData.append('file', blob, 'face.jpg');

            try {
                await api.post('/face/register', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
                setMessage('Face registered successfully!');
                setTimeout(() => navigate('/dashboard'), 2000);
            } catch (err) {
                setMessage('Failed to register face. Try again.');
            }
        }, 'image/jpeg');
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
            <h1 className="text-3xl font-bold mb-8">Register Your Face</h1>

            <div className="relative bg-black rounded-lg overflow-hidden shadow-2xl mb-6" style={{ width: 640, height: 480 }}>
                {!isStreaming && (
                    <div className="absolute inset-0 flex items-center justify-center">
                        <button
                            onClick={startCamera}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-full flex items-center gap-2 transition"
                        >
                            <Camera /> Start Camera
                        </button>
                    </div>
                )}
                <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    className="w-full h-full object-cover"
                />
                <canvas ref={canvasRef} width="640" height="480" className="hidden" />
            </div>

            {isStreaming && (
                <button
                    onClick={captureAndRegister}
                    className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-bold text-lg transition shadow-lg"
                >
                    Capture & Register
                </button>
            )}

            {message && (
                <div className={`mt-4 p-4 rounded ${message.includes('success') ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                    {message}
                </div>
            )}
        </div>
    );
}

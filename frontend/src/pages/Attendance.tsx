import { useRef, useState, useEffect } from 'react';
import { api } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';

export default function Attendance() {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [status, setStatus] = useState<'idle' | 'scanning' | 'success' | 'failed'>('idle');
    const [userName, setUserName] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        startCamera();
        return () => stopCamera();
    }, []);

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                setStatus('scanning');
                startScanning();
            }
        } catch (err) {
            console.error(err);
        }
    };

    const stopCamera = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
            tracks.forEach(track => track.stop());
        }
    };

    const startScanning = () => {
        const interval = setInterval(async () => {
            if (status === 'success') {
                clearInterval(interval);
                return;
            }
            await scanFace();
        }, 3000); // Scan every 3 seconds

        return () => clearInterval(interval);
    };

    const scanFace = async () => {
        if (!videoRef.current || !canvasRef.current) return;

        const context = canvasRef.current.getContext('2d');
        if (!context) return;

        context.drawImage(videoRef.current, 0, 0, 640, 480);

        canvasRef.current.toBlob(async (blob) => {
            if (!blob) return;

            const formData = new FormData();
            formData.append('file', blob, 'scan.jpg');

            try {
                const response = await api.post('/face/recognize', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });

                if (response.data) {
                    setUserName(response.data.full_name);
                    await markAttendance();
                    setStatus('success');
                    setTimeout(() => navigate('/dashboard'), 3000);
                }
            } catch (err) {
                // Keep scanning
            }
        }, 'image/jpeg');
    };

    const markAttendance = async () => {
        try {
            await api.post('/attendance/mark');
        } catch (err) {
            console.error('Failed to mark attendance');
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
            <h1 className="text-3xl font-bold mb-8">Mark Attendance</h1>

            <div className="relative bg-black rounded-lg overflow-hidden shadow-2xl mb-6" style={{ width: 640, height: 480 }}>
                <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    className="w-full h-full object-cover"
                />
                <canvas ref={canvasRef} width="640" height="480" className="hidden" />

                {status === 'success' && (
                    <div className="absolute inset-0 bg-green-500/80 flex flex-col items-center justify-center animate-fade-in">
                        <CheckCircle className="w-24 h-24 text-white mb-4" />
                        <h2 className="text-3xl font-bold">Welcome, {userName}!</h2>
                        <p className="text-xl mt-2">Attendance Marked</p>
                    </div>
                )}
            </div>

            <div className="text-gray-400">
                {status === 'scanning' ? 'Scanning face...' : status === 'success' ? 'Redirecting...' : 'Initializing camera...'}
            </div>
        </div>
    );
}

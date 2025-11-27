// import { useState } from 'react';
import { logout } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { LogOut, Camera, UserPlus, History } from 'lucide-react';
import AnalyticsDashboard from '../components/AnalyticsDashboard';

export default function Dashboard() {
    const navigate = useNavigate();
    // const [stats, setStats] = useState<any>(null);

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-6xl mx-auto">
                <div className="flex justify-between items-center mb-12">
                    <h1 className="text-3xl font-bold">Dashboard</h1>
                    <div className="flex gap-3">
                        <button
                            onClick={() => navigate('/admin')}
                            className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded transition"
                        >
                            Admin Panel
                        </button>
                        <button
                            onClick={logout}
                            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition"
                        >
                            <LogOut size={20} /> Logout
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    <div
                        onClick={() => navigate('/mark-attendance')}
                        className="bg-gray-800 p-6 rounded-xl cursor-pointer hover:bg-gray-750 transition border border-gray-700 hover:border-blue-500 group"
                    >
                        <div className="bg-blue-500/10 w-16 h-16 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-500/20 transition">
                            <Camera className="text-blue-500 w-8 h-8" />
                        </div>
                        <h3 className="text-xl font-semibold mb-2">Mark Attendance</h3>
                        <p className="text-gray-400">Use face recognition to check in</p>
                    </div>

                    <div
                        onClick={() => navigate('/register-face')}
                        className="bg-gray-800 p-6 rounded-xl cursor-pointer hover:bg-gray-750 transition border border-gray-700 hover:border-purple-500 group"
                    >
                        <div className="bg-purple-500/10 w-16 h-16 rounded-lg flex items-center justify-center mb-4 group-hover:bg-purple-500/20 transition">
                            <UserPlus className="text-purple-500 w-8 h-8" />
                        </div>
                        <h3 className="text-xl font-semibold mb-2">Register Face</h3>
                        <p className="text-gray-400">Update your face model</p>
                    </div>

                    <div
                        className="bg-gray-800 p-6 rounded-xl cursor-pointer hover:bg-gray-750 transition border border-gray-700 hover:border-green-500 group"
                    >
                        <div className="bg-green-500/10 w-16 h-16 rounded-lg flex items-center justify-center mb-4 group-hover:bg-green-500/20 transition">
                            <History className="text-green-500 w-8 h-8" />
                        </div>
                        <h3 className="text-xl font-semibold mb-2">History</h3>
                        <p className="text-gray-400">View your attendance records</p>
                    </div>
                </div>

                {/* Analytics Section */}
                <div className="mb-8">
                    <h2 className="text-2xl font-bold mb-6">Your Analytics</h2>
                    {/* Pass dummy user ID for now, in real app use actual user ID */}
                    <AnalyticsDashboard userId="current-user-id" />
                </div>
            </div>
        </div>
    );
}

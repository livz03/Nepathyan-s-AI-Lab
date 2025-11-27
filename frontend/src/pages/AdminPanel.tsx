import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Users, UserCheck, UserX, Settings, BarChart3 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function AdminPanel() {
    const [stats, setStats] = useState<any>(null);
    const [members, setMembers] = useState<any[]>([]);
    const [todayAttendance, setTodayAttendance] = useState<any[]>([]);
    const navigate = useNavigate();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [statsRes, membersRes, attendanceRes] = await Promise.all([
                api.get('/admin/stats'),
                api.get('/admin/members'),
                api.get('/admin/attendance/today')
            ]);

            setStats(statsRes.data);
            setMembers(membersRes.data);
            setTodayAttendance(attendanceRes.data);
        } catch (error) {
            console.error('Error fetching admin data:', error);
        }
    };

    const approveMember = async (userId: string) => {
        try {
            await api.post(`/admin/members/${userId}/approve`);
            fetchData();
        } catch (error: any) {
            alert(error.response?.data?.detail || 'Error approving member');
        }
    };

    const removeMember = async (userId: string) => {
        if (!confirm('Are you sure you want to remove this member?')) return;

        try {
            await api.delete(`/admin/members/${userId}`);
            fetchData();
        } catch (error) {
            alert('Error removing member');
        }
    };

    if (!stats) return <div>Loading...</div>;

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold">Admin Panel</h1>
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded"
                    >
                        Back to Dashboard
                    </button>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-gray-400 text-sm">Total Admins</p>
                                <h3 className="text-2xl font-bold">{stats.total_admins}/{stats.max_admins}</h3>
                            </div>
                            <Users className="w-8 h-8 text-blue-500" />
                        </div>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-gray-400 text-sm">Total Members</p>
                                <h3 className="text-2xl font-bold">{stats.total_members}/{stats.max_members}</h3>
                            </div>
                            <Users className="w-8 h-8 text-purple-500" />
                        </div>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-gray-400 text-sm">Present Today</p>
                                <h3 className="text-2xl font-bold">{stats.present_today}</h3>
                            </div>
                            <UserCheck className="w-8 h-8 text-green-500" />
                        </div>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-gray-400 text-sm">Absent Today</p>
                                <h3 className="text-2xl font-bold">{stats.total_members - stats.present_today}</h3>
                            </div>
                            <UserX className="w-8 h-8 text-red-500" />
                        </div>
                    </div>
                </div>

                {/* Members Table */}
                <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-8">
                    <h2 className="text-xl font-bold mb-4">Member Management</h2>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-700">
                                    <th className="text-left p-3">Name</th>
                                    <th className="text-left p-3">Email</th>
                                    <th className="text-left p-3">Phone</th>
                                    <th className="text-left p-3">Status</th>
                                    <th className="text-left p-3">Attendance</th>
                                    <th className="text-left p-3">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {members.map((member) => (
                                    <tr key={member._id} className="border-b border-gray-700">
                                        <td className="p-3">{member.name}</td>
                                        <td className="p-3">{member.email}</td>
                                        <td className="p-3">{member.phone || 'N/A'}</td>
                                        <td className="p-3">
                                            <span className={`px-2 py-1 rounded text-xs ${member.is_active ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                                                }`}>
                                                {member.is_active ? 'Active' : 'Pending'}
                                            </span>
                                        </td>
                                        <td className="p-3">{member.total_attendance || 0} days</td>
                                        <td className="p-3">
                                            {!member.is_active && (
                                                <button
                                                    onClick={() => approveMember(member._id)}
                                                    className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm mr-2"
                                                >
                                                    Approve
                                                </button>
                                            )}
                                            <button
                                                onClick={() => removeMember(member._id)}
                                                className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm"
                                            >
                                                Remove
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Today's Attendance */}
                <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <h2 className="text-xl font-bold mb-4">Today's Attendance</h2>
                    <div className="space-y-2">
                        {todayAttendance.map((record) => (
                            <div key={record._id} className="flex justify-between items-center p-3 bg-gray-700/50 rounded">
                                <div>
                                    <p className="font-semibold">{record.user_name}</p>
                                    <p className="text-sm text-gray-400">Check-in: {new Date(record.check_in).toLocaleTimeString()}</p>
                                </div>
                                <div className="text-right">
                                    {record.check_out ? (
                                        <p className="text-sm text-gray-400">Check-out: {new Date(record.check_out).toLocaleTimeString()}</p>
                                    ) : (
                                        <span className="text-green-400">Active</span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

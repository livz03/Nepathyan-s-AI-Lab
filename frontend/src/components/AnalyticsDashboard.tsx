import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, TrendingUp, AlertTriangle, Brain } from 'lucide-react';
import PatternBadge from './PatternBadge';

interface AnalyticsData {
    anomaly_score: number;
    pattern: string;
    streak: number;
    total_days: number;
}

interface AnalyticsDashboardProps {
    userId: string;
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ userId }) => {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [insight, setInsight] = useState<string>("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Mock API calls for now if backend isn't fully ready or data is missing
                // In production, replace with actual API calls
                // const analyticsRes = await axios.get(`http://localhost:8000/api/v1/analytics/user/${userId}`);
                // setData(analyticsRes.data);

                // const insightRes = await axios.get(`http://localhost:8000/api/v1/ai/insights/${userId}`);
                // setInsight(insightRes.data.insight);

                // Mock Data for UI Demo
                setData({
                    anomaly_score: 0.15,
                    pattern: "Early Bird",
                    streak: 12,
                    total_days: 45
                });
                setInsight("Great job maintaining a consistent schedule! You've been arriving before 9 AM for the last 5 days. Keep up the streak!");

            } catch (error) {
                console.error("Error fetching analytics:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [userId]);

    if (loading) return <div>Loading Analytics...</div>;
    if (!data) return <div>No data available</div>;

    // Mock Chart Data
    const chartData = [
        { name: 'Mon', time: 530 },
        { name: 'Tue', time: 540 },
        { name: 'Wed', time: 525 },
        { name: 'Thu', time: 535 },
        { name: 'Fri', time: 520 },
    ];

    return (
        <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex justify-between items-start">
                        <div>
                            <p className="text-sm text-gray-500">Current Streak</p>
                            <h3 className="text-2xl font-bold text-gray-900">{data.streak} Days</h3>
                        </div>
                        <div className="p-2 bg-orange-50 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-orange-500" />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex justify-between items-start">
                        <div>
                            <p className="text-sm text-gray-500">Pattern</p>
                            <div className="mt-1">
                                <PatternBadge pattern={data.pattern} />
                            </div>
                        </div>
                        <div className="p-2 bg-blue-50 rounded-lg">
                            <Activity className="w-5 h-5 text-blue-500" />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex justify-between items-start">
                        <div>
                            <p className="text-sm text-gray-500">Anomaly Score</p>
                            <h3 className={`text-2xl font-bold ${data.anomaly_score > 0.7 ? 'text-red-600' : 'text-green-600'}`}>
                                {data.anomaly_score.toFixed(2)}
                            </h3>
                        </div>
                        <div className={`p-2 rounded-lg ${data.anomaly_score > 0.7 ? 'bg-red-50' : 'bg-green-50'}`}>
                            <AlertTriangle className={`w-5 h-5 ${data.anomaly_score > 0.7 ? 'text-red-500' : 'text-green-500'}`} />
                        </div>
                    </div>
                </div>
            </div>

            {/* Charts & AI Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Chart */}
                <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Arrival Trends</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="name" />
                                <YAxis domain={[500, 600]} hide />
                                <Tooltip />
                                <Line type="monotone" dataKey="time" stroke="#4F46E5" strokeWidth={2} dot={{ r: 4 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* AI Insights */}
                <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-6 rounded-xl shadow-lg text-white relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Brain className="w-32 h-32" />
                    </div>
                    <div className="relative z-10">
                        <div className="flex items-center space-x-2 mb-4">
                            <Brain className="w-6 h-6" />
                            <h3 className="text-lg font-semibold">AI Insights</h3>
                        </div>
                        <p className="text-indigo-100 leading-relaxed">
                            {insight}
                        </p>
                        <button className="mt-6 w-full py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors backdrop-blur-sm">
                            Generate New Report
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsDashboard;

import React from 'react';
import { Sun, Moon, Clock, CheckCircle } from 'lucide-react';

interface PatternBadgeProps {
    pattern: string;
}

const PatternBadge: React.FC<PatternBadgeProps> = ({ pattern }) => {
    let color = "bg-gray-100 text-gray-800";
    let icon = <Clock className="w-4 h-4 mr-1" />;

    switch (pattern) {
        case "Early Bird":
            color = "bg-green-100 text-green-800 border-green-200";
            icon = <Sun className="w-4 h-4 mr-1" />;
            break;
        case "Night Owl":
            color = "bg-purple-100 text-purple-800 border-purple-200";
            icon = <Moon className="w-4 h-4 mr-1" />;
            break;
        case "Consistent":
            color = "bg-blue-100 text-blue-800 border-blue-200";
            icon = <CheckCircle className="w-4 h-4 mr-1" />;
            break;
        default:
            color = "bg-gray-100 text-gray-800 border-gray-200";
            icon = <Clock className="w-4 h-4 mr-1" />;
    }

    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${color}`}>
            {icon}
            {pattern}
        </span>
    );
};

export default PatternBadge;

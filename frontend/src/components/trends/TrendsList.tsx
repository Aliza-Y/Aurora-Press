import { useState } from 'react';
import { IconCheck } from '@tabler/icons-react';

interface Trend {
  id: string;
  keyword: string;
  category: string;
  source: string;
  type: string;
}

interface TrendsListProps {
  trends: Trend[];
  onApproveTrend: (trendId: string) => void;
}

const categories = [
  'All',
  'Politics',
  'Technology',
  'Science',
  'Business',
  'Entertainment',
  'Sports',
];

const TrendsList = ({ trends, onApproveTrend }: TrendsListProps) => {
  const [selectedCategory, setSelectedCategory] = useState('All');

  const filteredTrends = selectedCategory === 'All'
    ? trends
    : trends.filter(trend => trend.category === selectedCategory);

  return (
    <div className="space-y-6">
      {/* Category Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {categories.map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              selectedCategory === category
                ? 'bg-aurora-primary text-white'
                : 'bg-aurora-card text-aurora-text-secondary hover:bg-aurora-secondary'
            }`}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Trends List */}
      <div className="grid gap-4">
        {filteredTrends.map(trend => (
          <div
            key={trend.id}
            className="bg-aurora-card rounded-xl p-6 flex items-center justify-between group hover:bg-aurora-secondary transition-colors"
          >
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <h3 className="text-lg font-medium text-aurora-text">
                  {trend.keyword}
                </h3>
                <span className="px-2 py-1 rounded-md bg-aurora-background text-aurora-text-secondary text-xs">
                  {trend.source}
                </span>
              </div>
              
              <div className="flex items-center gap-4 text-sm text-aurora-text-secondary">
                <span>Category: {trend.category}</span>
                <span>Type: {trend.type}</span>
              </div>
            </div>

            <button
              onClick={() => onApproveTrend(trend.id)}
              className="ml-4 p-2 rounded-lg bg-aurora-primary/10 text-aurora-primary hover:bg-aurora-primary hover:text-white transition-colors"
              title="Approve Topic"
            >
              <IconCheck size={20} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrendsList; 
import React from 'react';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';
import { Box, Typography, Card, CardContent } from '@mui/material';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

interface PieChartProps {
  title: string;
  labels: string[];
  values: number[];
  colors?: string[];
  height?: number;
}

const PieChart: React.FC<PieChartProps> = ({
  title,
  labels,
  values,
  colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0'],
  height = 300
}) => {
  const data = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: colors,
        borderColor: colors.map(c => c),
        borderWidth: 1,
      },
    ],
  };

  const options: ChartOptions<'pie'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 15,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = context.dataset.data.reduce((acc: number, curr) => acc + (curr as number), 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} (${percentage}%)`;
          }
        }
      }
    },
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ height, position: 'relative' }}>
          <Pie data={data} options={options} />
        </Box>
      </CardContent>
    </Card>
  );
};

export default PieChart;

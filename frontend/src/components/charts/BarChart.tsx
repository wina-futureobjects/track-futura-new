import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';
import { Box, Typography, Card, CardContent } from '@mui/material';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface Dataset {
  label: string;
  data: number[];
  backgroundColor: string;
  borderColor?: string;
  borderWidth?: number;
}

interface BarChartProps {
  title: string;
  labels: string[];
  datasets: Dataset[];
  height?: number;
  stacked?: boolean;
}

const BarChart: React.FC<BarChartProps> = ({
  title,
  labels,
  datasets,
  height = 300,
  stacked = false
}) => {
  const data = {
    labels,
    datasets: datasets.map(dataset => ({
      ...dataset,
      borderColor: dataset.borderColor || dataset.backgroundColor,
      borderWidth: dataset.borderWidth || 1
    }))
  };

  const options: ChartOptions<'bar'> = {
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
        mode: 'index' as const,
        intersect: false,
      }
    },
    scales: {
      x: {
        stacked,
        grid: {
          display: false
        }
      },
      y: {
        stacked,
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      }
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ height, position: 'relative' }}>
          <Bar data={data} options={options} />
        </Box>
      </CardContent>
    </Card>
  );
};

export default BarChart;

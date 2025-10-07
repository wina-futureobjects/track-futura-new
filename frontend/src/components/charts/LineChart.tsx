import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ChartOptions
} from 'chart.js';
import { Box, Typography, Card, CardContent } from '@mui/material';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface Dataset {
  label: string;
  data: number[];
  borderColor: string;
  backgroundColor?: string;
  fill?: boolean;
  tension?: number;
}

interface LineChartProps {
  title: string;
  labels: (string | number)[];
  datasets: Dataset[];
  height?: number;
}

const LineChart: React.FC<LineChartProps> = ({
  title,
  labels,
  datasets,
  height = 300
}) => {
  const data = {
    labels,
    datasets: datasets.map(dataset => ({
      ...dataset,
      tension: dataset.tension !== undefined ? dataset.tension : 0.4,
      fill: dataset.fill !== undefined ? dataset.fill : false,
      backgroundColor: dataset.backgroundColor || dataset.borderColor,
      borderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
    }))
  };

  const options: ChartOptions<'line'> = {
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
        grid: {
          display: false
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      }
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ height, position: 'relative' }}>
          <Line data={data} options={options} />
        </Box>
      </CardContent>
    </Card>
  );
};

export default LineChart;

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { Box, Paper, Typography, Link, Stack } from '@mui/material';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ChartProps {
  type: 'line' | 'bar';
  data: ChartData<'line' | 'bar'>;
  title?: string;
  description?: React.ReactNode;
  onOpenChart?: () => void;
}

const defaultOptions: ChartOptions<'line' | 'bar'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          // Show value with comma separator
          let label = context.dataset.label || '';
          if (label) label += ': ';
          if (context.parsed.y !== null) label += context.parsed.y.toLocaleString();
          return label;
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.1)'
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
};

const ChatChart: React.FC<ChartProps> = ({ type, data, title, description, onOpenChart }) => {
  return (
    <Paper 
      elevation={0} 
      sx={{ 
        p: 0, 
        borderRadius: 3, 
        bgcolor: '#fff',
        border: '1px solid #e2e8f0',
        boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
        width: '100%',
        maxWidth: 700,
        mx: 'auto',
        my: 2
      }}
    >
      <Box sx={{ p: 3, pb: 2, borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#1e293b' }}>{title}</Typography>
        <Link
          href="#"
          underline="hover"
          sx={{ fontSize: 14, color: '#2563eb', fontWeight: 500 }}
          onClick={onOpenChart}
        >
          Open Chart
        </Link>
      </Box>
      <Box sx={{ px: 3, pt: 2, pb: 1, minHeight: 320 }}>
        {type === 'line' ? (
          <Line data={data as ChartData<'line'>} options={defaultOptions} />
        ) : (
          <Bar data={data as ChartData<'bar'>} options={defaultOptions} />
        )}
      </Box>
      {description && (
        <Box sx={{ px: 3, pb: 3, pt: 1 }}>
          {description}
        </Box>
      )}
    </Paper>
  );
};

export default ChatChart; 
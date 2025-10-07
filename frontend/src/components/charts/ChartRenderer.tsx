import React from 'react';
import PieChart from './PieChart';
import BarChart from './BarChart';
import LineChart from './LineChart';
import { Box, Typography, Alert } from '@mui/material';

interface VisualizationData {
  type: 'pie' | 'bar' | 'line';
  title: string;
  data: {
    labels: (string | number)[];
    values?: number[];
    datasets?: Array<{
      label: string;
      data: number[];
      backgroundColor: string;
      borderColor?: string;
      fill?: boolean;
    }>;
    colors?: string[];
  };
}

interface ChartRendererProps {
  visualization: VisualizationData;
  height?: number;
}

const ChartRenderer: React.FC<ChartRendererProps> = ({ visualization, height = 300 }) => {
  const { type, title, data } = visualization;

  // Debug logging
  console.log('🎨 ChartRenderer received:', { type, title, hasData: !!data });

  try {
    switch (type) {
      case 'pie':
        if (!data.labels || !data.values) {
          return (
            <Alert severity="warning">
              Missing data for pie chart: {title}
            </Alert>
          );
        }
        return (
          <PieChart
            title={title}
            labels={data.labels as string[]}
            values={data.values}
            colors={data.colors}
            height={height}
          />
        );

      case 'bar':
        if (!data.labels || !data.datasets) {
          return (
            <Alert severity="warning">
              Missing data for bar chart: {title}
            </Alert>
          );
        }
        return (
          <BarChart
            title={title}
            labels={data.labels as string[]}
            datasets={data.datasets}
            height={height}
          />
        );

      case 'line':
        if (!data.labels || !data.datasets) {
          return (
            <Alert severity="warning">
              Missing data for line chart: {title}
            </Alert>
          );
        }
        return (
          <LineChart
            title={title}
            labels={data.labels}
            datasets={data.datasets}
            height={height}
          />
        );

      default:
        return (
          <Alert severity="error">
            Unknown chart type: {type}
          </Alert>
        );
    }
  } catch (error) {
    console.error('Error rendering chart:', error);
    return (
      <Alert severity="error">
        Failed to render chart: {title}
      </Alert>
    );
  }
};

export default ChartRenderer;

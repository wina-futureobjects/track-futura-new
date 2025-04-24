import React from 'react';
import { Box, Typography, Paper, Button } from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Public as PublicIcon,
  Chat as ChatIcon,
  PeopleAlt as PeopleAltIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import StatCard from '../components/dashboard/StatCard';
import SentimentChart from '../components/charts/SentimentChart';
import WordCloudChart from '../components/charts/WordCloudChart';
import NPSChart from '../components/charts/NPSChart';

const Dashboard: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom fontWeight={700}>
            Digital Presence Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Overview of your brand's digital presence and sentiment analysis
          </Typography>
        </Box>
        <Button variant="outlined" color="primary">
          Export Report
        </Button>
      </Box>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Box sx={{ flex: '1 1 220px', minWidth: { xs: '100%', sm: 'calc(50% - 16px)', md: 'calc(25% - 18px)' } }}>
          <StatCard
            title="Social Mentions"
            value="8,540"
            icon={<ChatIcon />}
            color="primary"
            change={{ value: 12.5, positive: true }}
          />
        </Box>
        <Box sx={{ flex: '1 1 220px', minWidth: { xs: '100%', sm: 'calc(50% - 16px)', md: 'calc(25% - 18px)' } }}>
          <StatCard
            title="Web Mentions"
            value="3,215"
            icon={<PublicIcon />}
            color="secondary"
            change={{ value: 8.3, positive: true }}
          />
        </Box>
        <Box sx={{ flex: '1 1 220px', minWidth: { xs: '100%', sm: 'calc(50% - 16px)', md: 'calc(25% - 18px)' } }}>
          <StatCard
            title="Sentiment Score"
            value="72%"
            icon={<TrendingUpIcon />}
            color="success"
            change={{ value: 5.2, positive: true }}
          />
        </Box>
        <Box sx={{ flex: '1 1 220px', minWidth: { xs: '100%', sm: 'calc(50% - 16px)', md: 'calc(25% - 18px)' } }}>
          <StatCard
            title="Audience Reach"
            value="1.2M"
            icon={<PeopleAltIcon />}
            color="info"
            change={{ value: 3.1, positive: false }}
          />
        </Box>
      </Box>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        <Box sx={{ flex: '1 1 auto', minWidth: { xs: '100%', md: 'calc(66.666% - 12px)' } }}>
          <SentimentChart />
        </Box>
        <Box sx={{ flex: '1 1 auto', minWidth: { xs: '100%', md: 'calc(33.333% - 12px)' } }}>
          <WordCloudChart />
        </Box>
        <Box sx={{ width: '100%', mt: 3 }}>
          <NPSChart />
        </Box>
      </Box>

      <Box sx={{ mt: 3 }}>
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Recent Analysis Activity</Typography>
            <Button variant="text" color="primary">
              View All
            </Button>
          </Box>

          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column',
            gap: 2
          }}>
            {[1, 2, 3].map((item) => (
              <Box 
                key={item}
                sx={{ 
                  display: 'flex',
                  alignItems: 'center',
                  p: 2,
                  borderRadius: 1,
                  bgcolor: 'background.default',
                  '&:hover': { bgcolor: 'action.hover' }
                }}
              >
                <Box 
                  sx={{ 
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: 'primary.light',
                    color: 'primary.contrastText',
                    borderRadius: '50%',
                    width: 40,
                    height: 40,
                    mr: 2,
                  }}
                >
                  <TimelineIcon />
                </Box>
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="subtitle2">
                    {item === 1 ? 'Social Media Analysis Completed' : 
                     item === 2 ? 'Web Presence Report Generated' : 
                     'Sentiment Analysis Updated'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {item === 1 ? 'Analysis of Twitter, Instagram, Facebook' : 
                     item === 2 ? 'Analysis of top 100 websites mentioning your brand' : 
                     'Updated sentiment across all platforms'}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {item === 1 ? '2 hours ago' : 
                   item === 2 ? 'Yesterday' : 
                   '3 days ago'}
                </Typography>
              </Box>
            ))}
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

export default Dashboard; 
import React, { useState, useRef, useEffect } from 'react';
import { 
  Container, 
  Paper, 
  Box, 
  Typography, 
  TextField, 
  IconButton, 
  Avatar, 
  Divider,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Grid as MuiGrid,
  Card,
  CardContent,
  Button,
  Collapse,
  Fade,
  Breadcrumbs,
  Link,
  Stack,
  Tooltip
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import BarChartIcon from '@mui/icons-material/BarChart';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CompareIcon from '@mui/icons-material/Compare';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import HomeIcon from '@mui/icons-material/Home';
import FolderIcon from '@mui/icons-material/Folder';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import RefreshIcon from '@mui/icons-material/Refresh';
import SettingsIcon from '@mui/icons-material/Settings';
import { chatService, type Message, type ChatThread } from '../services/chatService';
import ChatChart from '../components/ChatChart';

// Fix for MUI Grid type issues with 'item' prop
const Grid = (props: any) => <MuiGrid {...props} />;

const Analysis: React.FC = () => {
  const [input, setInput] = useState<string>('');
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentThread, setCurrentThread] = useState<ChatThread | null>(null);
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasAsked = messages.length > 0;

  // Load threads on mount
  useEffect(() => {
    loadThreads();
  }, []);

  // Load messages when thread changes
  useEffect(() => {
    if (currentThread) {
      loadThreadMessages(currentThread.id);
    } else {
      setMessages([]);
    }
  }, [currentThread]);

  // Scroll to bottom of messages when a new message is added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadThreads = async () => {
    try {
      const threadsData = await chatService.getThreads();
      setThreads(Array.isArray(threadsData) ? threadsData : []);
      // Set current thread to the most recent active thread if exists
      const activeThread = Array.isArray(threadsData) ? threadsData.find(t => t.is_active) : null;
      if (activeThread) {
        setCurrentThread(activeThread);
      }
    } catch (error) {
      console.error('Failed to load threads:', error);
      setThreads([]);
    }
  };

  const loadThreadMessages = async (threadId: string) => {
    try {
      const thread = await chatService.getThread(threadId);
      setMessages(thread.messages || []);
    } catch (error) {
      console.error('Failed to load thread messages:', error);
      setMessages([]);
    }
  };

  const handleThreadSelect = async (thread: ChatThread) => {
    setCurrentThread(thread);
    setShowSuggestions(false);
  };

  const createNewThread = async () => {
    try {
      const newThread = await chatService.createThread();
      setThreads(prev => [newThread, ...(Array.isArray(prev) ? prev : [])]);
      setCurrentThread(newThread);
      setMessages([]);
      setShowSuggestions(true);
    } catch (error) {
      console.error('Failed to create thread:', error);
    }
  };

  // Function to parse and render a table from markdown-like text
  const renderTable = (tableText: string) => {
    const lines = tableText.trim().split('\n');
    if (lines.length < 3) return null; // Need at least header, separator, and one row
    
    // Parse header row
    const headers = lines[0].split('|').map(cell => cell.trim()).filter(cell => cell);
    
    // Skip separator row (line[1])
    
    // Parse data rows
    const rows = lines.slice(2).map(line => 
      line.split('|').map(cell => cell.trim()).filter(cell => cell)
    );
    
    return (
      <TableContainer component={Paper} sx={{ my: 2, boxShadow: 'none', border: '1px solid rgba(0,0,0,0.1)' }}>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ backgroundColor: 'rgba(0,0,0,0.04)' }}>
              {headers.map((header, index) => (
                <TableCell key={index} sx={{ fontWeight: 'bold' }}>
                  {header}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <TableCell key={cellIndex}>
                    {cell}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  // Function to generate a chart description summary (MVP, static for now)
  const getChartDescription = () => (
    <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mt: 1 }}>
      <Typography component="span" sx={{ fontSize: 13, bgcolor: '#f1f5f9', px: 1.5, py: 0.5, borderRadius: 1, mr: 1 }}>
        Measuring <b>number of unique Users</b>
      </Typography>
      <Typography component="span" sx={{ fontSize: 13, bgcolor: '#f1f5f9', px: 1.5, py: 0.5, borderRadius: 1, mr: 1 }}>
        that perform <b>Any Active Event</b>
      </Typography>
      <Typography component="span" sx={{ fontSize: 13, bgcolor: '#f1f5f9', px: 1.5, py: 0.5, borderRadius: 1, mr: 1 }}>
        for <b>All Users</b>
      </Typography>
      <Typography component="span" sx={{ fontSize: 13, bgcolor: '#f1f5f9', px: 1.5, py: 0.5, borderRadius: 1, mr: 1 }}>
        grouped by <b>Country</b> <b>weekly</b>
      </Typography>
      <Typography component="span" sx={{ fontSize: 13, bgcolor: '#f1f5f9', px: 1.5, py: 0.5, borderRadius: 1 }}>
        over the <b>Last 12 weeks</b>
      </Typography>
    </Stack>
  );

  // Function to convert markdown-like text to formatted content
  const formatMessageText = (text: string, sender: string) => {
    // Check if the text contains a chart data
    const chartDataMatch = text.match(/```chart\n([\s\S]*?)\n```/);
    
    if (chartDataMatch) {
      try {
        const chartData = JSON.parse(chartDataMatch[1]);
        const beforeChart = text.substring(0, chartDataMatch.index);
        const afterChart = text.substring((chartDataMatch.index || 0) + chartDataMatch[0].length);
        return (
          <>
            {sender === 'ai' && (
              <Typography variant="subtitle2" sx={{ color: '#64748b', mb: 1, fontWeight: 600 }}>
                Here's the chart you requested.
              </Typography>
            )}
            {beforeChart.split('\n').map((line, lineIndex) => (
              <React.Fragment key={`before-${lineIndex}`}>{line && <>{line}<br /></>}</React.Fragment>
            ))}
            <ChatChart
              type={chartData.type}
              data={chartData.data}
              title={chartData.title}
              description={getChartDescription()}
            />
            {afterChart.split('\n').map((line, lineIndex) => (
              <React.Fragment key={`after-${lineIndex}`}>{line && <>{line}<br /></>}</React.Fragment>
            ))}
          </>
        );
      } catch (error) {
        console.error('Failed to parse chart data:', error);
        return text;
      }
    }
    
    // Check if the text contains a table
    const tableRegex = /^([^|]+\|[^|]+\|.+\n)([-|]+\n)([^|]+\|[^|]+\|.+\n)+/m;
    const tableMatch = text.match(tableRegex);
    
    if (tableMatch) {
      // Split text into parts: before table, table, and after table
      const tableStart = tableMatch.index || 0;
      const tableEnd = tableStart + tableMatch[0].length;
      
      const beforeTable = text.substring(0, tableStart);
      const tableText = text.substring(tableStart, tableEnd);
      const afterTable = text.substring(tableEnd);
      
      return (
        <>
          {beforeTable.split('\n').map((line, lineIndex) => (
            <React.Fragment key={`before-${lineIndex}`}>
              {line.startsWith('##') ? (
                <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
                  {line.replace(/^##\s+/, '')}
                </Typography>
              ) : (
                line
              )}
              {line && <br />}
            </React.Fragment>
          ))}
          {renderTable(tableText)}
          {afterTable.split('\n').map((line, lineIndex) => (
            <React.Fragment key={`after-${lineIndex}`}>
              {line}
              {lineIndex < afterTable.split('\n').length - 1 && <br />}
            </React.Fragment>
          ))}
        </>
      );
    }
    
    // If no chart or table, format text normally with improved heading handling
    return text.split('\n').map((line, lineIndex) => (
      <React.Fragment key={lineIndex}>
        {line.startsWith('##') ? (
          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
            {line.replace(/^##\s+/, '')}
          </Typography>
        ) : (
          line || ' ' // Replace empty lines with a space
        )}
        {lineIndex < text.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  // Updated suggested questions with icons
  const suggestedQuestions = [
    {
      icon: <BarChartIcon sx={{ fontSize: 24, color: '#2563eb' }} />,
      text: "What insights can I get from my social media data?",
      description: "Analyze your social media performance metrics"
    },
    {
      icon: <TrendingUpIcon sx={{ fontSize: 24, color: '#2563eb' }} />,
      text: "How to identify trends in my Instagram performance?",
      description: "Track engagement and growth patterns"
    },
    {
      icon: <CompareIcon sx={{ fontSize: 24, color: '#2563eb' }} />,
      text: "Compare engagement rates between platforms",
      description: "Cross-platform performance analysis"
    },
    {
      icon: <MonetizationOnIcon sx={{ fontSize: 24, color: '#2563eb' }} />,
      text: "What metrics should I focus on for ROI?",
      description: "Key metrics for business impact"
    }
  ];

  // Handle sending a message
  const handleSendMessage = async () => {
    if (input.trim() === '' || !currentThread) return;
    
    try {
      setIsLoading(true);
      
      // Add user message
      const userMessage = await chatService.addMessage(currentThread.id, input, 'user');
      setMessages(prev => [...prev, userMessage]);
      setInput('');
      
      // Simulate AI response (would be replaced with actual AI service call)
      const aiResponse = await mockAIResponse(input);
      const aiMessage = await chatService.addMessage(currentThread.id, aiResponse, 'ai');
      setMessages(prev => [...prev, aiMessage]);
      
      // Refresh current thread to get latest state
      const updatedThread = await chatService.getThread(currentThread.id);
      setCurrentThread(updatedThread);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle keyboard press (Enter to send)
  const handleKeyPress = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle clicking a suggested question
  const handleSuggestedQuestion = (question: string) => {
    setInput(question);
  };

  const toggleSuggestions = () => {
    setShowSuggestions(!showSuggestions);
  };

  // Mock AI response function (to be replaced with actual AI service)
  const mockAIResponse = async (userInput: string): Promise<string> => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    let aiResponse = '';
    
    if (userInput.toLowerCase().includes('insights') || userInput.toLowerCase().includes('data')) {
      aiResponse = `
## Social Media Data Insights

Here are key insights available from your social media data:

1. Engagement Metrics
   - Likes, comments, shares trends
   - Peak engagement times
   - Most engaging content types

2. Audience Analysis
   - Follower growth rate
   - Demographic breakdown
   - Active followers vs total followers

3. Content Performance
   - Top performing posts
   - Content type effectiveness
   - Hashtag performance

Here's a visualization of your engagement trends:

\`\`\`chart
{
  "type": "line",
  "title": "Engagement Trends Over Time",
  "data": {
    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "datasets": [
      {
        "label": "Likes",
        "data": [1200, 1900, 1500, 2100, 1800, 2400],
        "borderColor": "#2563eb",
        "backgroundColor": "rgba(37, 99, 235, 0.1)"
      },
      {
        "label": "Comments",
        "data": [300, 450, 380, 520, 480, 600],
        "borderColor": "#7c3aed",
        "backgroundColor": "rgba(124, 58, 237, 0.1)"
      }
    ]
  }
}
\`\`\`

Would you like me to analyze any specific aspect in detail?
      `;
    } else if (userInput.toLowerCase().includes('trends') || userInput.toLowerCase().includes('instagram')) {
      aiResponse = `
## Instagram Performance Trends

Based on your recent Instagram data:

1. Growth Metrics
   - 15% increase in follower count
   - 23% higher engagement rate
   - 45% more profile visits

2. Content Trends
   - Reels outperforming static posts
   - Educational content getting more saves
   - Behind-the-scenes posts driving engagement

3. Audience Behavior
   - Peak activity: 6-8pm weekdays
   - Strong response to story polls
   - High engagement with carousel posts

Here's a breakdown of your content performance:

\`\`\`chart
{
  "type": "bar",
  "title": "Content Type Performance",
  "data": {
    "labels": ["Reels", "Posts", "Stories", "Carousels"],
    "datasets": [
      {
        "label": "Engagement Rate",
        "data": [4.8, 3.2, 2.9, 4.1],
        "backgroundColor": [
          "rgba(37, 99, 235, 0.8)",
          "rgba(124, 58, 237, 0.8)",
          "rgba(236, 72, 153, 0.8)",
          "rgba(14, 165, 233, 0.8)"
        ]
      }
    ]
  }
}
\`\`\`

Would you like to focus on any of these areas?
      `;
    } else if (userInput.toLowerCase().includes('compare') || userInput.toLowerCase().includes('engagement')) {
      aiResponse = `
## Cross-Platform Engagement Analysis

Here's how your engagement rates compare:

1. Instagram
   - 4.2% average engagement rate
   - Highest on Reels and Carousels
   - Strong comment-to-like ratio

2. Facebook
   - 2.8% average engagement rate
   - Best performance on video content
   - High share rate on infographics

3. LinkedIn
   - 3.5% average engagement rate
   - Strong performance on industry insights
   - High-quality professional discussions

Here's a comparison of your platform performance:

\`\`\`chart
{
  "type": "bar",
  "title": "Platform Engagement Comparison",
  "data": {
    "labels": ["Instagram", "Facebook", "LinkedIn"],
    "datasets": [
      {
        "label": "Engagement Rate",
        "data": [4.2, 2.8, 3.5],
        "backgroundColor": [
          "rgba(37, 99, 235, 0.8)",
          "rgba(124, 58, 237, 0.8)",
          "rgba(14, 165, 233, 0.8)"
        ]
      }
    ]
  }
}
\`\`\`

Would you like a detailed breakdown of any platform?
      `;
    } else if (userInput.toLowerCase().includes('roi') || userInput.toLowerCase().includes('metrics')) {
      aiResponse = `
## Key ROI Metrics to Track

For measuring social media ROI, focus on these metrics:

1. Conversion Rate: Track how many followers become customers
2. Customer Acquisition Cost (CAC): Cost to gain a new customer 
3. Lifetime Value (LTV): Average revenue from a customer over time
4. Engagement-to-Conversion Ratio: How engagement translates to sales

Here's a visualization of your ROI metrics:

\`\`\`chart
{
  "type": "line",
  "title": "ROI Metrics Over Time",
  "data": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "datasets": [
      {
        "label": "Conversion Rate",
        "data": [2.1, 2.8, 3.2, 3.5],
        "borderColor": "#2563eb",
        "backgroundColor": "rgba(37, 99, 235, 0.1)"
      },
      {
        "label": "CAC",
        "data": [45, 42, 38, 35],
        "borderColor": "#7c3aed",
        "backgroundColor": "rgba(124, 58, 237, 0.1)"
      }
    ]
  }
}
\`\`\`

Would you like me to help set up a custom ROI tracking dashboard for your specific business goals?
      `;
    } else {
      aiResponse = `Thank you for your question about "${userInput.substring(0, 30)}...". 

This is a demo of the AI analysis assistant. In a production environment, I would connect to your data sources to provide personalized insights about your social media performance, audience engagement, and content strategy.

Feel free to ask about Instagram, Facebook, or metrics performance to see sample responses.`;
    }
    
    return aiResponse;
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f8fafc', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar */}
      <Box
        sx={{
          width: 270,
          bgcolor: '#fff',
          borderRight: '1px solid #e2e8f0',
          display: 'flex',
          flexDirection: 'column',
          p: 0,
          minHeight: '100vh',
          height: '100vh',
        }}
      >
        <Box sx={{ p: 3, borderBottom: '1px solid #e2e8f0' }}>
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#1e293b', mb: 2 }}>
            Ask Track Futura
          </Typography>
          <Button
            variant="contained"
            onClick={createNewThread}
            sx={{
              bgcolor: '#2563eb',
              color: 'white',
              borderRadius: 1.5,
              textTransform: 'none',
              fontWeight: 600,
              boxShadow: 'none',
              width: '100%',
              mb: 2,
              '&:hover': { bgcolor: '#1d4ed8' }
            }}
          >
            + New thread
          </Button>
        </Box>
        <Box sx={{ flex: 1, p: 3, overflowY: 'auto', minHeight: 0 }}>
          <Stack spacing={2}>
            <Typography variant="overline" sx={{ color: '#64748b', letterSpacing: 1 }}>
              Today
            </Typography>
            {threads.map((thread) => (
              <Button
                key={thread.id}
                variant="text"
                onClick={() => handleThreadSelect(thread)}
                sx={{
                  justifyContent: 'flex-start',
                  textAlign: 'left',
                  textTransform: 'none',
                  color: '#1e293b',
                  p: 1.5,
                  borderRadius: 1,
                  bgcolor: currentThread?.id === thread.id ? '#f1f5f9' : 'transparent',
                  '&:hover': { bgcolor: '#f1f5f9' }
                }}
              >
                <Typography noWrap sx={{ fontSize: '0.875rem' }}>
                  {thread.title || thread.last_message?.content.split('\n')[0].substring(0, 35) + '...' || 'New Thread'}
                </Typography>
              </Button>
            ))}
          </Stack>
        </Box>
      </Box>

      {/* Main content area */}
      <Box sx={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        position: 'relative', 
        height: '100vh', 
        minHeight: 0,
        width: 'calc(100% - 270px)', // Add fixed width based on sidebar
        transition: 'width 0.2s ease-in-out' // Add smooth transition
      }}>
        {/* Initial view with suggestions */}
        {!hasAsked && showSuggestions && (
          <>
            <Box sx={{ p: 8, textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#1e293b', mb: 4 }}>
                What do you want to learn today?
              </Typography>
              <Box sx={{ maxWidth: 800, mx: 'auto', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 3 }}>
                {suggestedQuestions.map((question, index) => (
                  <Paper
                    key={index}
                    onClick={() => handleSuggestedQuestion(question.text)}
                    sx={{
                      p: 3,
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                      }
                    }}
                  >
                    {question.icon}
                    <Typography variant="h6" sx={{ mt: 2, mb: 1, color: '#1e293b', fontWeight: 600 }}>
                      {question.text}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#64748b' }}>
                      {question.description}
                    </Typography>
                  </Paper>
                ))}
              </Box>
            </Box>
          </>
        )}
        {/* Chat area */}
        {(hasAsked || !showSuggestions) && (
          <Box sx={{ 
            width: '100%', 
            flex: 1, 
            display: 'flex', 
            flexDirection: 'column', 
            pt: 8, 
            pb: 0, 
            minHeight: 0,
            position: 'relative' // Add position relative
          }}>
            {/* Messages - scrollable area */}
            <Box
              sx={{
                flex: 1,
                overflowY: 'auto',
                pb: 2,
                minHeight: 0,
                maxHeight: 'calc(100vh - 110px - 48px)',
                width: '100%', // Ensure full width
                position: 'relative' // Add position relative
              }}
            >
              <Box sx={{ 
                width: '100%', 
                maxWidth: 900, 
                mx: 'auto',
                px: 2 // Add some padding for the content
              }}>
                {messages.map((message) => (
                  <Fade in={true} key={message.id}>
                    <Box
                      sx={{
                        display: 'flex',
                        flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                        gap: 2,
                        maxWidth: '100%',
                        alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
                        mb: 3
                      }}
                    >
                      {/* User avatar only for user messages */}
                      {message.sender === 'user' && (
                        <Avatar
                          sx={{
                            width: 32,
                            height: 32,
                            bgcolor: '#2563eb',
                            color: 'white'
                          }}
                        >
                          <PersonIcon />
                        </Avatar>
                      )}
                      <Box sx={{ flex: 1, maxWidth: message.sender === 'ai' ? 900 : 600 }}>
                        {/* Remove Paper for AI, keep for user */}
                        {message.sender === 'user' ? (
                          <Paper
                            elevation={0}
                            sx={{
                              p: 2,
                              borderRadius: 2,
                              bgcolor: '#2563eb',
                              color: 'white',
                              border: 'none',
                              fontSize: '1rem',
                              lineHeight: 1.7
                            }}
                          >
                            {message.content}
                          </Paper>
                        ) : (
                          <Box
                            sx={{
                              fontSize: '1.05rem',
                              lineHeight: 1.8,
                              color: '#1e293b',
                              px: 0,
                              py: 0.5,
                              background: 'none',
                              borderRadius: 0,
                              fontWeight: 400
                            }}
                          >
                            {formatMessageText(message.content, message.sender)}
                          </Box>
                        )}
                        <Typography variant="caption" sx={{ color: '#94a3b8', mt: 0.5, textAlign: message.sender === 'user' ? 'right' : 'left' }}>
                          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </Typography>
                      </Box>
                    </Box>
                  </Fade>
                ))}
                {isLoading && (
                  <Box sx={{ display: 'flex', gap: 2, maxWidth: '80%' }}>
                    <Avatar sx={{ width: 32, height: 32, bgcolor: '#f1f5f9', color: '#2563eb' }}>
                      <SmartToyIcon />
                    </Avatar>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        bgcolor: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1
                      }}
                    >
                      <CircularProgress size={16} sx={{ color: '#2563eb' }} />
                      <Typography variant="body2" sx={{ color: '#64748b' }}>
                        Analyzing...
                      </Typography>
                    </Paper>
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </Box>
            </Box>
          </Box>
        )}
        {/* Input bar at the bottom */}
        <Box sx={{ position: 'absolute', left: 0, right: 0, bottom: 0, bgcolor: 'transparent', zIndex: 10, px: 0, pb: 3 }}>
          <Box sx={{ maxWidth: 1200, mx: 'auto', width: '100%' }}>
            <Paper elevation={2} sx={{ borderRadius: 99, px: 2, py: 1, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TextField
                  fullWidth
                  placeholder="Ask a question"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyPress}
                  variant="standard"
                  InputProps={{
                    disableUnderline: true,
                    sx: { fontSize: '1.1rem', pl: 1, bgcolor: 'transparent' }
                  }}
                />
                <IconButton
                  color="primary"
                  onClick={handleSendMessage}
                  disabled={input.trim() === '' || isLoading || !currentThread}
                  sx={{
                    bgcolor: '#2563eb',
                    color: 'white',
                    ml: 1,
                    '&:hover': { bgcolor: '#1d4ed8' },
                    '&.Mui-disabled': { bgcolor: '#94a3b8', color: 'white' },
                    width: 40,
                    height: 40
                  }}
                >
                  <SendIcon sx={{ fontSize: 22 }} />
                </IconButton>
              </Box>
            </Paper>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default Analysis; 
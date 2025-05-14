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
  TableRow
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';

// Types for chat messages
interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  displayContent?: string; // Content to be displayed (for typewriter effect)
  isTyping?: boolean; // Whether the typewriter effect is in progress
}

const Analysis: React.FC = () => {
  const [input, setInput] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      content: "Hello! I'm your AI assistant. Ask me anything about your project or data analysis needs.",
      sender: 'ai',
      timestamp: new Date(),
      displayContent: "Hello! I'm your AI assistant. Ask me anything about your project or data analysis needs.",
      isTyping: false
    }
  ]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimerRef = useRef<number | null>(null);

  // Scroll to bottom of messages when a new message is added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle typewriter effect for messages
  useEffect(() => {
    // Find the first message that is still typing
    const typingMessage = messages.find(msg => msg.isTyping && msg.sender === 'ai');
    
    if (typingMessage) {
      const fullContent = typingMessage.content;
      const currentDisplayContent = typingMessage.displayContent || '';
      
      if (currentDisplayContent.length < fullContent.length) {
        // Clear any existing timeout
        if (typingTimerRef.current) {
          window.clearTimeout(typingTimerRef.current);
        }
        
        // Set a timeout to update the display content
        typingTimerRef.current = window.setTimeout(() => {
          // Make typing faster by adding multiple characters at once
          const charsToAdd = 5; // Number of characters to add per tick
          const endPos = Math.min(currentDisplayContent.length + charsToAdd, fullContent.length);
          const newDisplayContent = fullContent.substring(0, endPos);
          
          setMessages(prevMessages => 
            prevMessages.map(msg => 
              msg.id === typingMessage.id 
                ? { 
                    ...msg, 
                    displayContent: newDisplayContent,
                    isTyping: newDisplayContent.length < fullContent.length 
                  } 
                : msg
            )
          );
        }, 10); // Faster speed of typing
      }
    }
    
    // Cleanup function
    return () => {
      if (typingTimerRef.current) {
        window.clearTimeout(typingTimerRef.current);
      }
    };
  }, [messages]);

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

  // Function to convert markdown-like text to formatted content
  const formatMessageText = (text: string) => {
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
    
    // If no table, format text normally with improved heading handling
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

  // Sample suggested questions that users can click on
  const suggestedQuestions = [
    "What insights can I get from my social media data?",
    "How to identify trends in my Instagram performance?",
    "Compare engagement rates between platforms",
    "What metrics should I focus on for ROI?"
  ];

  // Handle sending a message
  const handleSendMessage = () => {
    if (input.trim() === '') return;
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: 'user',
      timestamp: new Date(),
      displayContent: input,
      isTyping: false
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    // Simulate AI response (would be replaced with actual API call)
    setTimeout(() => {
      mockAIResponse(input);
      setIsLoading(false);
    }, 1500);
  };

  // Mock AI response generation based on user input
  const mockAIResponse = (userInput: string) => {
    let aiResponse: string;
    
    // Simple pattern matching for demo purposes
    if (userInput.toLowerCase().includes('instagram') || userInput.toLowerCase().includes('ig')) {
      aiResponse = `
## Instagram Performance Analysis

Based on the data collected, here are some insights for your Instagram accounts:

- Engagement Rate: Your engagement rate is 3.2% (industry average is 2.8%)
- Top Performing Content: Posts with lifestyle photos receive 42% more likes
- Growth Rate: You've gained 1,200 followers in the last 30 days (+5.3%)
- Best Posting Time: Wednesdays at 6pm generates the most engagement

Would you like more specific analysis about your Instagram content strategy or audience demographics?
      `;
    } else if (userInput.toLowerCase().includes('facebook') || userInput.toLowerCase().includes('fb')) {
      aiResponse = `
## Facebook Analytics Overview

Your Facebook performance shows:

- Reach: 45,200 people reached in the last month (+12% MoM)
- Click-through Rate: 1.8% (industry average is 1.2%)
- Audience Demographics: 62% female, 38% male, mostly aged 25-34
- Content Types: Video content performs 3.2x better than static images

I recommend focusing more on video content and posting during peak hours (12-2pm).
      `;
    } else if (userInput.toLowerCase().includes('compare') || userInput.toLowerCase().includes('comparison')) {
      aiResponse = `
## Platform Comparison

Metric | Instagram | Facebook | LinkedIn | TikTok
------ | --------- | -------- | -------- | ------
Engagement Rate | 3.2% | 1.7% | 2.1% | 5.4%
Audience Growth | +5.3% | +2.1% | +3.8% | +12.6%
Avg. Reach | 12,500 | 45,200 | 8,700 | 38,600
Click-through | 2.3% | 1.8% | 3.4% | 1.5%

TikTok shows the highest growth potential, while LinkedIn has the best conversion rate. Would you like recommendations for any specific platform?
      `;
    } else if (userInput.toLowerCase().includes('roi') || userInput.toLowerCase().includes('metrics')) {
      aiResponse = `
## Key ROI Metrics to Track

For measuring social media ROI, focus on these metrics:

1. Conversion Rate: Track how many followers become customers
2. Customer Acquisition Cost (CAC): Cost to gain a new customer 
3. Lifetime Value (LTV): Average revenue from a customer over time
4. Engagement-to-Conversion Ratio: How engagement translates to sales

Would you like me to help set up a custom ROI tracking dashboard for your specific business goals?
      `;
    } else {
      aiResponse = `Thank you for your question about "${userInput.substring(0, 30)}...". 

This is a demo of the AI analysis assistant. In a production environment, I would connect to your data sources to provide personalized insights about your social media performance, audience engagement, and content strategy.

Feel free to ask about Instagram, Facebook, or metrics performance to see sample responses.`;
    }
    
    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: aiResponse,
      sender: 'ai',
      timestamp: new Date(),
      displayContent: '', // Start with empty display content
      isTyping: true // Start typing animation
    };
    
    setMessages(prev => [...prev, aiMessage]);
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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper 
        elevation={3}
        sx={{ 
          height: 'calc(100vh - 160px)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          borderRadius: 2
        }}
      >
        {/* Chat header */}
        <Box sx={{ 
          p: 2, 
          backgroundColor: 'primary.main', 
          color: 'white',
          borderTopLeftRadius: 8,
          borderTopRightRadius: 8,
          display: 'flex',
          alignItems: 'center'
        }}>
          <SmartToyIcon sx={{ mr: 1 }} />
          <Typography variant="h6">Analysis Assistant</Typography>
        </Box>
        
        {/* Messages container */}
        <Box sx={{ 
          flexGrow: 1, 
          overflowY: 'auto', 
          p: 2,
          backgroundColor: 'background.default'
        }}>
          {messages.map((message) => (
            <Box 
              key={message.id}
              sx={{ 
                display: 'flex',
                mb: 2,
                flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
              }}
            >
              <Avatar 
                sx={{ 
                  bgcolor: message.sender === 'user' ? 'primary.main' : 'secondary.main',
                  mr: message.sender === 'user' ? 0 : 1,
                  ml: message.sender === 'user' ? 1 : 0,
                }}
              >
                {message.sender === 'user' ? <PersonIcon /> : <SmartToyIcon />}
              </Avatar>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  maxWidth: '75%',
                  borderRadius: 2,
                  backgroundColor: message.sender === 'user' ? 'primary.light' : 'white',
                  color: message.sender === 'user' ? 'white' : 'text.primary',
                  whiteSpace: 'pre-line',
                  fontFamily: 'inherit',
                }}
              >
                <Box sx={{ 
                  fontSize: '1rem'
                }}>
                  {message.isTyping ? (
                    <>
                      {formatMessageText(message.displayContent || '')}
                      <span className="cursor">|</span>
                    </>
                  ) : (
                    formatMessageText(message.content)
                  )}
                </Box>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    display: 'block', 
                    mt: 1,
                    opacity: 0.7, 
                    textAlign: message.sender === 'user' ? 'right' : 'left' 
                  }}
                >
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Typography>
              </Paper>
            </Box>
          ))}
          {isLoading && (
            <Box sx={{ display: 'flex', my: 2 }}>
              <Avatar sx={{ bgcolor: 'secondary.main', mr: 1 }}>
                <SmartToyIcon />
              </Avatar>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  borderRadius: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  minWidth: 60
                }}
              >
                <CircularProgress size={20} />
              </Paper>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>
        
        {/* Suggested questions */}
        {messages.length < 3 && (
          <Box sx={{ p: 2, backgroundColor: 'background.paper' }}>
            <Typography variant="subtitle2" gutterBottom>
              Try asking:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {suggestedQuestions.map((question, index) => (
                <Chip
                  key={index}
                  label={question}
                  onClick={() => handleSuggestedQuestion(question)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </Box>
        )}
        
        <Divider />
        
        {/* Input area */}
        <Box sx={{ p: 2, backgroundColor: 'background.paper', display: 'flex' }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Ask a question about your project data..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            variant="outlined"
            InputProps={{
              sx: { borderRadius: 3 }
            }}
          />
          <IconButton 
            color="primary" 
            onClick={handleSendMessage} 
            disabled={input.trim() === '' || isLoading}
            sx={{ ml: 1 }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </Container>
  );
};

export default Analysis; 
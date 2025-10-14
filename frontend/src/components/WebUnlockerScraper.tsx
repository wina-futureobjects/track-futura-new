// Web Unlocker Integration Component
import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { Box, TextField, Button, Typography, Card, CardContent, List, ListItem, ListItemText, CircularProgress } from '@mui/material';

const WebUnlockerScraper = () => {
    const [url, setUrl] = useState('');
    const [scraperName, setScraperName] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleScrape = async () => {
        if (!url) {
            toast.error('Please enter a URL to scrape');
            return;
        }

        setIsLoading(true);

        try {
            const response = await fetch('/api/web-unlocker/scrape/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({
                    url: url,
                    scraper_name: scraperName || 'Web Unlocker'
                })
            });

            const data = await response.json();

            if (data.success) {
                toast.success(`Scraping completed! Data stored in folder ID: ${data.folder_id}`);
                toast.info(`Data size: ${data.data_size} characters`);
                
                // Reset form
                setUrl('');
                setScraperName('');
                
                // Refresh data storage page
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                toast.error(`Scraping failed: ${data.error}`);
            }
        } catch (error) {
            toast.error(`Network error: ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    const getCsrfToken = () => {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                     document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                     '';
        return token;
    };

    return (
        <Card sx={{ mb: 3, bgcolor: 'white', boxShadow: 2 }}>
            <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" component="h3" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                    🔓 Web Unlocker Scraper
                </Typography>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <TextField
                        label="Target URL *"
                        type="url"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="https://example.com"
                        disabled={isLoading}
                        fullWidth
                        variant="outlined"
                    />
                    
                    <TextField
                        label="Scraper Name (Optional)"
                        type="text"
                        value={scraperName}
                        onChange={(e) => setScraperName(e.target.value)}
                        placeholder="My Web Scraper"
                        disabled={isLoading}
                        fullWidth
                        variant="outlined"
                    />
                    
                    <Button
                        onClick={handleScrape}
                        disabled={isLoading || !url}
                        variant="contained"
                        color="primary"
                        fullWidth
                        size="large"
                        sx={{ py: 1.5 }}
                    >
                        {isLoading ? (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <CircularProgress size={20} color="inherit" />
                                Scraping...
                            </Box>
                        ) : (
                            '🚀 Start Scraping'
                        )}
                    </Button>
                </Box>
                
                <Box sx={{ mt: 3, p: 2, bgcolor: 'primary.50', borderRadius: 1, border: '1px solid', borderColor: 'primary.200' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.800', mb: 1 }}>
                        How it works:
                    </Typography>
                    <List dense sx={{ py: 0 }}>
                        <ListItem sx={{ py: 0, px: 0 }}>
                            <ListItemText primary="• Enter any URL you want to scrape" sx={{ color: 'primary.700', '& .MuiListItemText-primary': { fontSize: '0.875rem' } }} />
                        </ListItem>
                        <ListItem sx={{ py: 0, px: 0 }}>
                            <ListItemText primary="• Web Unlocker bypasses anti-bot protection" sx={{ color: 'primary.700', '& .MuiListItemText-primary': { fontSize: '0.875rem' } }} />
                        </ListItem>
                        <ListItem sx={{ py: 0, px: 0 }}>
                            <ListItemText primary="• Data is automatically stored in your data storage" sx={{ color: 'primary.700', '& .MuiListItemText-primary': { fontSize: '0.875rem' } }} />
                        </ListItem>
                        <ListItem sx={{ py: 0, px: 0 }}>
                            <ListItemText primary="• Results appear instantly in your dashboard" sx={{ color: 'primary.700', '& .MuiListItemText-primary': { fontSize: '0.875rem' } }} />
                        </ListItem>
                    </List>
                </Box>
            </CardContent>
        </Card>
    );
};

export default WebUnlockerScraper;
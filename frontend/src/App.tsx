import React, { useState, useEffect, useRef } from 'react';
import { Container, Box, TextField, Typography, Paper, List, ListItem, ListItemText, Button, CircularProgress } from '@mui/material';
import { sendMessageToAI } from './api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // פונקציית שליחת ההודעה
  const handleSend = async (textToSend: string, finished: boolean = false) => {
    if (!textToSend.trim() && !finished) return;

    const newMessages: Message[] = [...messages, { role: 'user', content: textToSend }];
    if (!finished) setMessages(newMessages);
    
    setLoading(true);
    setInputText(''); // איפוס שדה ההקלדה
    
    try {
      const aiResponse = await sendMessageToAI(newMessages, finished);
      setMessages([...newMessages, { role: 'assistant', content: aiResponse }]);
      if (finished) setIsFinished(true);
    } catch (error) {
      console.error("Error calling AI:", error);
    } finally {
      setLoading(false);
    }
  };

  // מנגנון זיהוי סיום הקלדה (Debounce)
  useEffect(() => {
    if (inputText.trim() === '' || isFinished) return;

    setIsTyping(true);

    // אם המשתמש מקליד, אנחנו מאפסים את הטיימר הקודם
    if (timerRef.current) clearTimeout(timerRef.current);

    // קובעים טיימר של 2 שניות - אם לא הוקלד כלום, נשלח אוטומטית
    timerRef.current = setTimeout(() => {
      setIsTyping(false);
      handleSend(inputText);
    }, 2000);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [inputText]);

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom align="center" sx={{ fontWeight: 'bold', color: '#1976d2' }}>
        סימולטור הכשרת נציגים - ביטוח ישיר
      </Typography>

      <Paper elevation={3} sx={{ height: '60vh', overflowY: 'auto', p: 2, mb: 2, backgroundColor: '#f5f5f5' }}>
        <List>
          {messages.map((msg, index) => (
            <ListItem key={index} sx={{ justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              <Paper sx={{ 
                p: 1.5, 
                backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#ffffff',
                borderRadius: msg.role === 'user' ? '15px 15px 0 15px' : '15px 15px 15px 0',
                maxWidth: '70%'
              }}>
                <ListItemText primary={msg.content} />
              </Paper>
            </ListItem>
          ))}
          {loading && <CircularProgress size={24} sx={{ m: 2 }} />}
        </List>
      </Paper>

      {!isFinished ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="הקלד את תשובת הנציג כאן... (התשובה תישלח אוטומטית לאחר 2 שניות של שקט)"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={loading}
            multiline
            rows={2}
          />
          <Typography variant="caption" color="textSecondary">
            {isTyping ? "הלקוח ממתין שתסיים לדבר..." : "מצב: מוכן לשמוע"}
          </Typography>
          
          <Button 
            variant="contained" 
            color="error" 
            onClick={() => handleSend(inputText, true)}
            disabled={loading}
          >
            סיום שיחה וקבלת משוב
          </Button>
        </Box>
      ) : (
        <Button variant="outlined" onClick={() => window.location.reload()}>שיחה חדשה</Button>
      )}
    </Container>
  );
};

export default App;
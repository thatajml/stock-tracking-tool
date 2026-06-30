import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import {
  Container,
  Typography,
  Box,
  Paper,
  Alert,
  CircularProgress,
  AppBar,
  Toolbar,
  LinearProgress,
  Grid,
  TextField,
  Collapse,
  Button,
  MenuList,
  MenuItem,
  Popper,
  ClickAwayListener,
  InputAdornment
} from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SearchIcon from '@mui/icons-material/Search';
import ChartComponent from './ChartComponent'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'

const NIFTY_50_STOCKS = [
  { ticker: "ADANIPORTS.NS", name: "Adani Ports and Special Economic Zone" },
  { ticker: "ASIANPAINT.NS", name: "Asian Paints" },
  { ticker: "AXISBANK.NS", name: "Axis Bank" },
  { ticker: "BAJAJ-AUTO.NS", name: "Bajaj Auto" },
  { ticker: "BAJFINANCE.NS", name: "Bajaj Finance" },
  { ticker: "BAJAJFINSV.NS", name: "Bajaj Finserv" },
  { ticker: "BEL.NS", name: "Bharat Electronics" },
  { ticker: "BHARTIARTL.NS", name: "Bharti Airtel" },
  { ticker: "CIPLA.NS", name: "Cipla" },
  { ticker: "COALINDIA.NS", name: "Coal India" },
  { ticker: "DRREDDY.NS", name: "Dr. Reddy's Laboratories" },
  { ticker: "EICHERMOT.NS", name: "Eicher Motors" },
  { ticker: "ETERNAL.NS", name: "Eternal" },
  { ticker: "GRASIM.NS", name: "Grasim Industries" },
  { ticker: "HCLTECH.NS", name: "HCL Technologies" },
  { ticker: "HDFCBANK.NS", name: "HDFC Bank" },
  { ticker: "HDFCLIFE.NS", name: "HDFC Life Insurance" },
  { ticker: "HEROMOTOCO.NS", name: "Hero MotoCorp" },
  { ticker: "HINDALCO.NS", name: "Hindalco Industries" },
  { ticker: "HINDUNILVR.NS", name: "Hindustan Unilever" },
  { ticker: "ICICIBANK.NS", name: "ICICI Bank" },
  { ticker: "INDUSINDBK.NS", name: "IndusInd Bank" },
  { ticker: "INFY.NS", name: "Infosys" },
  { ticker: "ITC.NS", name: "ITC" },
  { ticker: "JIOFIN.NS", name: "Jio Financial Services" },
  { ticker: "JSWSTEEL.NS", name: "JSW Steel" },
  { ticker: "KOTAKBANK.NS", name: "Kotak Mahindra Bank" },
  { ticker: "LT.NS", name: "Larsen & Toubro" },
  { ticker: "M&M.NS", name: "Mahindra & Mahindra" },
  { ticker: "MARUTI.NS", name: "Maruti Suzuki India" },
  { ticker: "NESTLEIND.NS", name: "Nestle India" },
  { ticker: "NTPC.NS", name: "NTPC" },
  { ticker: "ONGC.NS", name: "Oil and Natural Gas Corporation" },
  { ticker: "POWERGRID.NS", name: "Power Grid Corporation of India" },
  { ticker: "RELIANCE.NS", name: "Reliance Industries" },
  { ticker: "SBILIFE.NS", name: "SBI Life Insurance" },
  { ticker: "SBIN.NS", name: "State Bank of India" },
  { ticker: "SHRIRAMFIN.NS", name: "Shriram Finance" },
  { ticker: "SUNPHARMA.NS", name: "Sun Pharmaceutical Industries" },
  { ticker: "TATACONSUM.NS", name: "Tata Consumer Products" },
  { ticker: "TATAMOTORS.NS", name: "Tata Motors" },
  { ticker: "TATASTEEL.NS", name: "Tata Steel" },
  { ticker: "TCS.NS", name: "Tata Consultancy Services" },
  { ticker: "TECHM.NS", name: "Tech Mahindra" },
  { ticker: "TITAN.NS", name: "Titan Company" },
  { ticker: "TRENT.NS", name: "Trent" },
  { ticker: "ULTRACEMCO.NS", name: "UltraTech Cement" },
  { ticker: "WIPRO.NS", name: "Wipro" },
  { ticker: "APOLLOHOSP.NS", name: "Apollo Hospitals Enterprise" },
  { ticker: "BAJAJHLDNG.NS", name: "Bajaj Holdings & Investment" },
]

function App() {
  const [stocks] = useState(NIFTY_50_STOCKS)
  const [selectedTicker, setSelectedTicker] = useState('')
  const [stockData, setStockData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showLogic, setShowLogic] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchText, setSearchText] = useState('')
  const searchAnchorRef = useRef(null)

  useEffect(() => {
    // Set first stock as default
    if (NIFTY_50_STOCKS.length > 0) {
      setSelectedTicker(NIFTY_50_STOCKS[0].ticker)
    }
  }, [])

  useEffect(() => {
    if (!selectedTicker) return

    setLoading(true)
    setError(null)

    axios.get(`${API_BASE_URL}/stock/${selectedTicker}`)
      .then(res => {
        setStockData(res.data)
      })
      .catch(err => {
        console.error("Error fetching stock data:", err)
        setError(`Failed to load data for ${selectedTicker}. Check if the given ticker symbol exists.`)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [selectedTicker])

  const getSignalColor = (signal) => {
    if (signal === 'Buy') return 'success'
    if (signal === 'Sell') return 'error'
    return 'warning'
  }

  // Convert the -100 to +100 score to a 0-100 percentage for the progress bar
  const getProgressValue = (score) => {
    return Math.max(0, Math.min(100, (score + 100) / 2));
  }

  const getProgressColor = (score) => {
    if (score >= 60) return "success"
    if (score <= -60) return "error"
    return "warning"
  }
  const getCategoryScore = (reasons) => {
    if (!reasons) return 0;
    return reasons.reduce((total, reason) => {
      const match = reason.match(/^([+-]?\s*\d+):/);
      if (match) {
        return total + parseInt(match[1].replace(/\s/g, ''), 10);
      }
      return total;
    }, 0);
  };

  return (
    <Box sx={{ flexGrow: 1, backgroundColor: '#f5f5f5', minHeight: '100vh', paddingBottom: 4 }}>
      <AppBar position="static" color="primary" elevation={0} sx={{ mb: 4 }}>
        <Toolbar>
          <TrendingUpIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            QuantSense Stock Signal Dashboard
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg">
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Quantitative Analysis{selectedTicker ? ` of ${stocks.find(s => s.ticker === selectedTicker)?.name || selectedTicker}` : ''}
          </Typography>

          <Box 
            ref={searchAnchorRef}
            onMouseEnter={() => setSearchOpen(true)} 
            onMouseLeave={() => setSearchOpen(false)}
            sx={{ position: 'relative' }}
          >
            <TextField
              id="stock-search"
              label="Search NSE Symbol (e.g. RELIANCE)"
              variant="outlined"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && searchText.trim()) {
                  const ticker = searchText.trim().toUpperCase();
                  setSelectedTicker(ticker.includes('.') ? ticker : `${ticker}.NS`);
                  setSearchOpen(false);
                  setSearchText('');
                }
              }}
              disabled={loading}
              sx={{ minWidth: 350 }}
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                },
              }}
              helperText="Hover to browse or type to search"
            />
            {searchOpen && (
              <Paper 
                elevation={8} 
                sx={{ 
                  position: 'absolute', 
                  top: '100%', 
                  left: 0, 
                  right: 0, 
                  zIndex: 1300, 
                  maxHeight: 300, 
                  overflow: 'auto',
                  mt: -2.5
                }}
              >
                <MenuList dense>
                  {stocks
                    .filter(s => {
                      if (!searchText) return true;
                      const input = searchText.toLowerCase();
                      return s.name.toLowerCase().includes(input) || s.ticker.toLowerCase().includes(input);
                    })
                    .map((stock) => (
                      <MenuItem 
                        key={stock.ticker} 
                        selected={stock.ticker === selectedTicker}
                        onClick={() => {
                          setSelectedTicker(stock.ticker);
                          setSearchOpen(false);
                          setSearchText('');
                        }}
                      >
                        {stock.name} ({stock.ticker})
                      </MenuItem>
                    ))
                  }
                  {stocks.filter(s => {
                    if (!searchText) return true;
                    const input = searchText.toLowerCase();
                    return s.name.toLowerCase().includes(input) || s.ticker.toLowerCase().includes(input);
                  }).length === 0 && (
                    <MenuItem disabled>No matches found</MenuItem>
                  )}
                </MenuList>
              </Paper>
            )}
          </Box>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 10 }}>
            <CircularProgress />
          </Box>
        ) : stockData ? (
          <>
            <Paper elevation={2} sx={{ p: 2, mb: 3, borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom>
                Historical Price & Volume (Daily)
              </Typography>
              <ChartComponent data={stockData.data} />
            </Paper>

            <Box sx={{ mb: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Button 
                variant="outlined" 
                onClick={() => setShowLogic(!showLogic)}
                sx={{ mb: 2 }}
              >
                {showLogic ? 'Hide Score Calculation' : 'Show Score Calculation'}
              </Button>
              <Collapse in={showLogic} sx={{ width: '100%' }}>
                <Paper elevation={1} sx={{ p: 2, bgcolor: '#ffffff', color: '#000000', borderRadius: 2, border: '1px solid #e0e0e0' }}>
                  <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', m: 0, mb: 2, whiteSpace: 'pre-wrap', bgcolor: '#f5f5f5', p: 1.5, borderRadius: 1 }}>
{`Initialize total_score = 0
Create four categories:
    Trend
    Momentum
    Timing
    Confirmation`}
                  </Typography>

                  <Box sx={{ 
                    display: 'grid', 
                    gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, 
                    gridAutoRows: '1fr',
                    gap: 2, mb: 2 
                  }}>
                    {/* Trend */}
                    <Box sx={{ border: '1px solid #e0e0e0', borderRadius: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                      <Box sx={{ bgcolor: '#9c27b0', color: 'white', py: 1, px: 1.5, textAlign: 'center' }}>
                        <Typography variant="subtitle2" fontWeight="bold">TREND (Maximum ±35 points)</Typography>
                      </Box>
                      <Box sx={{ p: 1.5, flexGrow: 1, bgcolor: '#ffffff' }}>
                        <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', m: 0, whiteSpace: 'pre-wrap', color: '#000000' }}>
{`IF Current Price > 20-day Simple Moving Average THEN
    Add 15 points
ELSE
    Subtract 15 points
END IF

IF ADX > 25 THEN
    IF +DI > -DI THEN
        Add 10 points
    ELSE
        Subtract 10 points
    END IF
ELSE
    Give 0 points
END IF

IF Ichimoku Cloud data exists THEN
    Find the upper boundary of the cloud
    Find the lower boundary of the cloud

    IF Price is above the cloud THEN
        Add 10 points
    ELSE IF Price is below the cloud THEN
        Subtract 10 points
    ELSE
        Give 0 points
    END IF
ELSE
    Give 0 points
END IF`}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Momentum */}
                    <Box sx={{ border: '1px solid #e0e0e0', borderRadius: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                      <Box sx={{ bgcolor: '#ed6c02', color: 'white', py: 1, px: 1.5, textAlign: 'center' }}>
                        <Typography variant="subtitle2" fontWeight="bold">MOMENTUM (Maximum ±25 points)</Typography>
                      </Box>
                      <Box sx={{ p: 1.5, flexGrow: 1, bgcolor: '#ffffff' }}>
                        <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', m: 0, whiteSpace: 'pre-wrap', color: '#000000' }}>
{`IF RSI is below 30
    OR
   RSI is between 40 and 60 AND rising
THEN
    Add 15 points
ELSE IF RSI is above 70
    OR
        RSI is between 40 and 60 AND falling
THEN
    Subtract 15 points
ELSE
    Give 0 points
END IF

IF Stochastic is below 20
AND Stochastic crosses above its signal line
THEN
    Add 10 points
ELSE IF Stochastic is above 80
AND Stochastic crosses below its signal line
THEN
    Subtract 10 points
ELSE
    Give 0 points
END IF`}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Timing */}
                    <Box sx={{ border: '1px solid #e0e0e0', borderRadius: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                      <Box sx={{ bgcolor: '#0288d1', color: 'white', py: 1, px: 1.5, textAlign: 'center' }}>
                        <Typography variant="subtitle2" fontWeight="bold">TIMING (Maximum ±20 points)</Typography>
                      </Box>
                      <Box sx={{ p: 1.5, flexGrow: 1, bgcolor: '#ffffff' }}>
                        <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', m: 0, whiteSpace: 'pre-wrap', color: '#000000' }}>
{`IF MACD is above its Signal Line THEN
    Add 10 points
ELSE
    Subtract 10 points
END IF

IF Price is above VWAP THEN
    Add 10 points
ELSE
    Subtract 10 points
END IF`}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Confirmation */}
                    <Box sx={{ border: '1px solid #e0e0e0', borderRadius: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                      <Box sx={{ bgcolor: '#2e7d32', color: 'white', py: 1, px: 1.5, textAlign: 'center' }}>
                        <Typography variant="subtitle2" fontWeight="bold">CONFIRMATION (Maximum ±20 points)</Typography>
                      </Box>
                      <Box sx={{ p: 1.5, flexGrow: 1, bgcolor: '#ffffff' }}>
                        <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', m: 0, whiteSpace: 'pre-wrap', color: '#000000' }}>
{`IF Bollinger Band data exists THEN
    Calculate Bollinger Band Width
    IF Price is near the Lower Band THEN
        Add 10 points
    ELSE IF Price is near the Upper Band THEN
        Subtract 10 points
    ELSE
        Give 0 points
    END IF
ELSE
    Give 0 points
END IF

IF Current Volume > Average 20-day Volume THEN
    IF Current Score is Positive THEN
        Add 10 points
    ELSE IF Current Score is Negative THEN
        Subtract 10 points
    ELSE
        Give 0 points
    END IF
ELSE
    Give 0 points
END IF`}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>

                  <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', m: 0, whiteSpace: 'pre-wrap', bgcolor: '#f5f5f5', p: 1.5, borderRadius: 1 }}>
{`FINAL DECISION
--------------------------------------------------
IF Total Score >= 60 THEN
    Signal = BUY
ELSE IF Total Score <= -60 THEN
    Signal = SELL
ELSE
    Signal = HOLD
END IF

Display:
    Total Score
    Buy / Hold / Sell Signal
    Explanation from each category`}
                  </Typography>
                </Paper>
              </Collapse>
            </Box>

            <Alert
              severity={getSignalColor(stockData.signal)}
              sx={{ py: 2, px: 3, mb: 3, borderRadius: 2 }}
              iconMapping={{
                success: <TrendingUpIcon fontSize="inherit" />,
              }}
            >
              <Box sx={{ mb: 2 }}>
                <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 1 }}>
                  Signal: {stockData.signal.toUpperCase()}
                  <Typography component="span" sx={{ ml: 2, color: 'text.secondary' }}>
                    Net Confidence Score: {stockData.score > 0 ? '+' : ''}{stockData.score}/100
                  </Typography>
                </Typography>

                <Box sx={{ width: '100%', mr: 1, mt: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Total Algorithmic Confidence (-100 to +100)
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={getProgressValue(stockData.score)}
                    color={getProgressColor(stockData.score)}
                    sx={{ height: 12, borderRadius: 5, mt: 0.5 }}
                  />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                    <Typography variant="caption" color="error" fontWeight="bold">HEAVY SELL</Typography>
                    <Typography variant="caption" color="warning.main" fontWeight="bold">HOLD RANGE</Typography>
                    <Typography variant="caption" color="success.main" fontWeight="bold">HEAVY BUY</Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1, fontFamily: 'monospace' }}>
                    Progress Bar Logic: Math.max(0, Math.min(100, (score + 100) / 2))
                  </Typography>
                </Box>
              </Box>
            </Alert>

            {/* 4 Organised Subsections for Signal Breakdown */}
            <Typography variant="h6" sx={{ mt: 4, mb: 2, fontWeight: 'bold', textAlign: 'center' }}>
              Algorithmic Breakdown by Sub-Section:
            </Typography>

            <Box sx={{ maxWidth: '1000px', margin: '0 auto' }}>
              <Paper elevation={0} sx={{ p: 2, mb: 3, border: '1px solid', borderColor: 'divider', borderRadius: 2, bgcolor: 'background.default' }}>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom color="text.secondary">
                  Scoring Logic Overview & Calculation
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
                  The final signal is determined by a cumulative score ranging from <strong>-100 to +100</strong> across four categories: 
                  Trend (35 pts), Momentum (25 pts), Timing (20 pts), and Confirmation (20 pts).
                  <br/>
                  <strong>Thresholds:</strong> Heavy Buy (≥ 60) | Hold (-59 to 59) | Heavy Sell (≤ -60).
                </Typography>
                {stockData.categories && (
                  <Box sx={{ p: 1.5, bgcolor: 'action.hover', borderRadius: 1, display: 'inline-block' }}>
                    <Typography variant="body2" fontWeight="bold" sx={{ fontFamily: 'monospace' }}>
                      Calculation: Trend ({getCategoryScore(stockData.categories.Trend)}) + Momentum ({getCategoryScore(stockData.categories.Momentum)}) + Timing ({getCategoryScore(stockData.categories.Timing)}) + Confirmation ({getCategoryScore(stockData.categories.Confirmation)}) = {stockData.score}
                    </Typography>
                  </Box>
                )}
              </Paper>

              {stockData.categories && (
                <Box 
                  sx={{ 
                    display: 'grid', 
                    gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, 
                    gridAutoRows: '1fr',
                    gap: 3 
                  }}
                >
                  {Object.entries(stockData.categories).map(([categoryName, reasons]) => {
                    // Assign colors based on category names for a premium look
                    let headerColor = '#1976d2';
                    if (categoryName === 'Trend') headerColor = '#9c27b0';
                    if (categoryName === 'Momentum') headerColor = '#ed6c02';
                    if (categoryName === 'Timing') headerColor = '#0288d1';
                    if (categoryName === 'Confirmation') headerColor = '#2e7d32';

                    return (
                      <Paper
                        key={categoryName}
                        elevation={3}
                        sx={{
                          height: '100%',
                          borderRadius: 2,
                          overflow: 'hidden',
                          display: 'flex',
                          flexDirection: 'column'
                        }}
                      >
                        <Box sx={{ bgcolor: headerColor, color: 'white', py: 1.5, px: 2, textAlign: 'center' }}>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {categoryName} Logic
                          </Typography>
                        </Box>
                        <Box sx={{ p: 2, flexGrow: 1, bgcolor: '#ffffff' }}>
                          <ul style={{ margin: 0, paddingLeft: '20px' }}>
                            {reasons.map((r, idx) => {
                              // Add subtle color coding to positive/negative scores
                              const isPositive = r.startsWith('+');
                              const isNegative = r.startsWith('-');
                              const textColor = isPositive ? 'success.main' : isNegative ? 'error.main' : 'text.primary';

                              return (
                                <li key={idx} style={{ marginBottom: '8px' }}>
                                  <Typography variant="body2" color={textColor} fontWeight={isPositive || isNegative ? 'medium' : 'regular'}>
                                    {r}
                                  </Typography>
                                </li>
                              );
                            })}
                          </ul>
                        </Box>
                      </Paper>
                    );
                  })}
                </Box>
              )}
            </Box>
          </>
        ) : (
          !loading && !error && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography color="text.secondary">Select a stock to view analysis.</Typography>
            </Paper>
          )
        )}
      </Container>
    </Box>
  )
}

export default App

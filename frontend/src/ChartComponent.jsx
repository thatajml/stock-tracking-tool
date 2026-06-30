import React, { useEffect, useRef } from 'react';
import { createChart, CrosshairMode } from 'lightweight-charts';
import { Box, Typography } from '@mui/material';

export default function ChartComponent({ data }) {
    const mainContainerRef = useRef();
    const volumeContainerRef = useRef();
    const momentumContainerRef = useRef();

    const chartRefs = useRef({});

    useEffect(() => {
        if (!data || data.length === 0) return;

        if (!chartRefs.current.main && mainContainerRef.current) {

            // --- MAIN CHART (Price, SMA, VWAP, BB, Ichimoku) ---
            const mainChart = createChart(mainContainerRef.current, {
                height: 400,
                layout: { background: { color: '#ffffff' }, textColor: '#333' },
                grid: { vertLines: { color: '#f0f3fa' }, horzLines: { color: '#f0f3fa' } },
                crosshair: { mode: CrosshairMode.Normal },
                rightPriceScale: { borderColor: '#dfdfdf' },
                timeScale: { visible: false } // Hide time scale on top charts
            });

            const ichiCloudSeries = mainChart.addCandlestickSeries({
                upColor: 'rgba(76, 175, 80, 0.25)', 
                downColor: 'rgba(244, 67, 54, 0.25)',
                borderVisible: false,
                wickVisible: false,
                lastValueVisible: false,
                priceLineVisible: false
            });

            const candlestickSeries = mainChart.addCandlestickSeries({
                upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
                wickUpColor: '#26a69a', wickDownColor: '#ef5350',
            });

            const smaSeries = mainChart.addLineSeries({ color: '#f5a623', lineWidth: 2, title: 'SMA 20' });
            const vwapSeries = mainChart.addLineSeries({ color: '#9c27b0', lineWidth: 2, title: 'VWAP' });

            const ichiASeries = mainChart.addLineSeries({ color: 'rgba(76, 175, 80, 0.8)', lineWidth: 1, lineStyle: 0, title: 'Ichimoku A', lastValueVisible: false, priceLineVisible: false });
            const ichiBSeries = mainChart.addLineSeries({ color: 'rgba(244, 67, 54, 0.8)', lineWidth: 1, lineStyle: 0, title: 'Ichimoku B', lastValueVisible: false, priceLineVisible: false });

            // --- VOLUME CHART ---
            const volumeChart = createChart(volumeContainerRef.current, {
                height: 150,
                layout: { background: { color: '#ffffff' }, textColor: '#333' },
                grid: { vertLines: { color: '#f0f3fa' }, horzLines: { color: '#f0f3fa' } },
                timeScale: { visible: false },
                rightPriceScale: { borderColor: '#dfdfdf' }
            });
            const volumeSeries = volumeChart.addHistogramSeries({
                color: '#26a69a', priceFormat: { type: 'volume' }, priceScaleId: ''
            });

            // --- MOMENTUM CHART (RSI, Stochastic, ADX) ---
            const momentumChart = createChart(momentumContainerRef.current, {
                height: 200,
                layout: { background: { color: '#ffffff' }, textColor: '#333' },
                grid: { vertLines: { color: '#f0f3fa' }, horzLines: { color: '#f0f3fa' } },
                timeScale: { borderColor: '#dfdfdf', timeVisible: true },
                rightPriceScale: { borderColor: '#dfdfdf' },
                leftPriceScale: { visible: true, borderColor: '#dfdfdf' }
            });

            const rsiSeries = momentumChart.addLineSeries({ color: '#9c27b0', lineWidth: 2, title: 'RSI', autoscaleInfoProvider: () => ({ priceRange: { minValue: 0, maxValue: 100 } }) });
            const stochSeries = momentumChart.addLineSeries({ color: '#2196f3', lineWidth: 1, title: 'Stoch%K' });
            const adxSeries = momentumChart.addLineSeries({ color: '#ff9800', lineWidth: 2, title: 'ADX' });

            // User asked to switch to MACD Histograms
            const macdHistSeries = momentumChart.addHistogramSeries({ 
                title: 'MACD Hist', 
                priceScaleId: 'left' 
            });

            // --- Syncing ---
            const syncTimeScale = (source, target1, target2) => {
                source.timeScale().subscribeVisibleLogicalRangeChange((range) => {
                    if (range) {
                        target1.timeScale().setVisibleLogicalRange(range);
                        target2.timeScale().setVisibleLogicalRange(range);
                    }
                });
            };

            if (mainChart.timeScale().subscribeVisibleLogicalRangeChange) {
                syncTimeScale(mainChart, volumeChart, momentumChart);
                syncTimeScale(momentumChart, mainChart, volumeChart);
            }

            chartRefs.current = {
                mainChart, volumeChart, momentumChart,
                ichiCloudSeries, candlestickSeries, smaSeries, vwapSeries, ichiASeries, ichiBSeries,
                volumeSeries, rsiSeries, stochSeries, adxSeries, macdHistSeries
            };

            const handleResize = () => {
                mainChart.applyOptions({ width: mainContainerRef.current.clientWidth });
                volumeChart.applyOptions({ width: volumeContainerRef.current.clientWidth });
                momentumChart.applyOptions({ width: momentumContainerRef.current.clientWidth });
            };

            window.addEventListener('resize', handleResize);

            return () => {
                window.removeEventListener('resize', handleResize);
                mainChart.remove();
                volumeChart.remove();
                momentumChart.remove();
                chartRefs.current = {};
            };
        }
    }, []);

    useEffect(() => {
        if (chartRefs.current.mainChart && data && data.length > 0) {
            const formattedData = [...data].sort((a, b) => new Date(a.time) - new Date(b.time));
            const uniqueData = Array.from(new Map(formattedData.map(item => [item.time, item])).values());

            const series = chartRefs.current;

            series.candlestickSeries.setData(uniqueData.map(i => ({ time: i.time, open: i.open, high: i.high, low: i.low, close: i.close })));

            series.volumeSeries.setData(uniqueData.map(i => ({ time: i.time, value: i.volume, color: i.close >= i.open ? '#26a69a' : '#ef5350' })));

            if (series.smaSeries) series.smaSeries.setData(uniqueData.filter(i => i.sma20 != null).map(i => ({ time: i.time, value: i.sma20 })));
            if (series.vwapSeries) series.vwapSeries.setData(uniqueData.filter(i => i.vwap != null).map(i => ({ time: i.time, value: i.vwap })));
            if (series.ichiASeries) series.ichiASeries.setData(uniqueData.filter(i => i.ichimoku_a != null).map(i => ({ time: i.time, value: i.ichimoku_a })));
            if (series.ichiBSeries) series.ichiBSeries.setData(uniqueData.filter(i => i.ichimoku_b != null).map(i => ({ time: i.time, value: i.ichimoku_b })));
            if (series.ichiCloudSeries) {
                series.ichiCloudSeries.setData(uniqueData.filter(i => i.ichimoku_a != null && i.ichimoku_b != null).map(i => ({
                    time: i.time,
                    open: i.ichimoku_b,
                    close: i.ichimoku_a,
                    high: Math.max(i.ichimoku_a, i.ichimoku_b),
                    low: Math.min(i.ichimoku_a, i.ichimoku_b)
                })));
            }

            if (series.rsiSeries) series.rsiSeries.setData(uniqueData.filter(i => i.rsi != null).map(i => ({ time: i.time, value: i.rsi })));
            if (series.stochSeries) series.stochSeries.setData(uniqueData.filter(i => i.stoch != null).map(i => ({ time: i.time, value: i.stoch })));
            if (series.adxSeries) series.adxSeries.setData(uniqueData.filter(i => i.adx != null).map(i => ({ time: i.time, value: i.adx })));
            if (series.macdHistSeries) series.macdHistSeries.setData(uniqueData.filter(i => i.macd_hist != null).map(i => ({ 
                time: i.time, 
                value: i.macd_hist, 
                color: i.macd_hist >= 0 ? 'rgba(38, 166, 154, 0.8)' : 'rgba(239, 83, 80, 0.8)' 
            })));

            series.mainChart.timeScale().fitContent();
        }
    }, [data]);

    return (
        <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <Box sx={{ width: '100%', position: 'relative' }}>
                <Typography variant="subtitle2" fontWeight="bold" sx={{ position: 'absolute', top: 5, left: 10, zIndex: 10, bgcolor: 'rgba(255,255,255,0.8)', px: 1, borderRadius: 1, pointerEvents: 'none' }}>
                    1. Price Action (Candles, SMA, VWAP, Ichimoku Cloud)
                </Typography>
                <Box ref={mainContainerRef} sx={{ width: '100%' }} />
            </Box>
            <Box sx={{ width: '100%', position: 'relative' }}>
                <Typography variant="caption" fontWeight="bold" sx={{ position: 'absolute', top: 5, left: 10, zIndex: 10, bgcolor: 'rgba(255,255,255,0.8)', px: 1, borderRadius: 1, pointerEvents: 'none' }}>
                    2. Volume Profile
                </Typography>
                <Box ref={volumeContainerRef} sx={{ width: '100%' }} />
            </Box>
            <Box sx={{ width: '100%', position: 'relative' }}>
                <Typography variant="caption" fontWeight="bold" sx={{ position: 'absolute', top: 5, left: 10, zIndex: 10, bgcolor: 'rgba(255,255,255,0.8)', px: 1, borderRadius: 1, pointerEvents: 'none' }}>
                    3. Momentum & Timing (RSI, Stoch, ADX) [Right] + MACD Histogram [Left]
                </Typography>
                <Box ref={momentumContainerRef} sx={{ width: '100%' }} />
            </Box>
        </Box>
    );
}

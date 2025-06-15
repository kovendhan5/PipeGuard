# PipeGuard Dashboard Screenshot Guide

This guide explains how to capture professional screenshots of the PipeGuard dashboard for documentation purposes.

## Prerequisites

1. **Start the development server:**
   ```bash
   python run_local.py
   # Select option 1: Start Flask Development Server
   ```

2. **Verify the server is running:**
   - Check terminal output for "Running on http://localhost:8080"
   - Wait for the message "Dashboard ready with sample data"

## Taking Screenshots

### 1. Access the Dashboard

Open your web browser and navigate to: `http://localhost:8080`

The dashboard will automatically load with sample data showing:
- Live statistics with trend indicators
- Interactive charts with real data
- AI-powered insights and recommendations
- Modern responsive design

### 2. Optimal Screenshot Settings

**Browser Setup:**
- Use a modern browser (Chrome, Firefox, Edge)
- Set window width to 1920px for desktop screenshots
- Use browser developer tools for mobile screenshots (375px width)
- Ensure zoom is set to 100%

**Screenshot Areas:**
- **Full Dashboard**: Capture the entire page including header, stats, and charts
- **Statistics Panel**: Focus on the top metrics cards with trend indicators
- **Charts Section**: Highlight the interactive dual-axis charts
- **AI Insights**: Capture the recommendations and anomaly detection panel

### 3. Screenshot Specifications

**Main Dashboard Screenshot:**
- File: `docs/images/performance-analytics-screenshot.png`
- Resolution: 1920x1080 (or fit content)
- Format: PNG with transparency support
- Compression: Optimize for web while maintaining quality

**Additional Screenshots (Optional):**
- `docs/images/mobile-dashboard.png` - Mobile responsive view
- `docs/images/charts-detail.png` - Detailed chart view
- `docs/images/ai-insights.png` - AI recommendations panel

### 4. Capturing Process

**Windows (Built-in):**
```bash
# Use Windows Snipping Tool or Snip & Sketch
# Press Win + Shift + S for screen capture
```

**Browser Extensions:**
- Full Page Screen Capture (Chrome)
- FireShot (Firefox)
- Awesome Screenshot (Cross-browser)

**Professional Tools:**
- Lightshot
- Greenshot
- Snagit

### 5. Post-Processing

**Image Optimization:**
- Crop to remove browser chrome if desired
- Ensure consistent aspect ratio
- Optimize file size for web (aim for <500KB)
- Add subtle drop shadow if needed for documentation

**Quality Checklist:**
- ✅ All text is readable
- ✅ Charts and data are visible
- ✅ Colors are vibrant and accurate
- ✅ No browser UI elements (unless intended)
- ✅ Professional appearance

## Using Screenshots in Documentation

### README.md Integration

Replace the existing placeholder in the README:
```markdown
![PipeGuard Performance Analytics](docs/images/performance-analytics-screenshot.png)
```

### Additional Documentation

Screenshots can be used in:
- Feature documentation
- Setup guides
- User manuals
- Presentation materials

## Sample Data Information

The development server includes realistic sample data:
- **Build Statistics**: 156 total builds, 94.2% success rate
- **Performance Metrics**: Average duration 4m 32s
- **Trend Indicators**: Shows improving/declining metrics
- **AI Insights**: Displays sample recommendations and anomalies

This ensures screenshots demonstrate the full functionality of the dashboard even without live pipeline data.

## Troubleshooting

**Common Issues:**

1. **Dashboard not loading:**
   - Check if Flask server is running on port 8080
   - Verify no firewall blocking localhost access
   - Try refreshing the browser page

2. **Sample data not appearing:**
   - Wait 5-10 seconds for data to load
   - Check browser console for JavaScript errors
   - Try a hard refresh (Ctrl+F5)

3. **Styling issues:**
   - Ensure CSS files are loading properly
   - Check for browser compatibility issues
   - Try different browser if problems persist

## Screenshot Updates

When updating screenshots:
1. Replace files in `docs/images/` directory
2. Maintain consistent naming convention
3. Update alt text in documentation if needed
4. Verify links work in markdown preview

---

**Note**: Screenshots should be updated when significant UI changes are made to ensure documentation accuracy.

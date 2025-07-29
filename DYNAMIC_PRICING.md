# Dynamic OpenAI Pricing Management

## Overview
The AI Chatbot now supports dynamic pricing management instead of hardcoded values, making it easier to keep OpenAI pricing up-to-date and accurate.

## ✅ Improvements Over Hardcoded Pricing

### Problems with Hardcoded Pricing:
- ❌ **Outdated quickly**: OpenAI changes pricing frequently
- ❌ **Manual updates required**: Need to edit code and redeploy
- ❌ **Error-prone**: Easy to miss model updates or new models
- ❌ **No transparency**: Users don't know if pricing is current

### Benefits of Dynamic Pricing:
- ✅ **Always current**: Load pricing from external sources
- ✅ **Easy updates**: Multiple update methods available
- ✅ **Transparent**: Shows pricing source and last update date
- ✅ **Flexible**: Supports manual and automated updates
- ✅ **Reliable**: Fallback to hardcoded values if needed

## 🛠️ Implementation Details

### 1. Configuration-Based System
- **Config File**: `config/openai_pricing.json`
- **Dynamic Loading**: Prices loaded at runtime from config
- **Fallback Safety**: Uses hardcoded prices if config unavailable

### 2. Multiple Update Methods

#### **Automated Updates (`update_pricing.py`)**
```bash
# Try all methods automatically
python update_pricing.py --method auto

# Specific methods
python update_pricing.py --method github      # Community repo
python update_pricing.py --method web_scrape  # OpenAI website
python update_pricing.py --method external_api # Third-party APIs
```

#### **Manual Updates**
```bash
# Edit config file directly
python update_pricing.py --method manual
# Then edit: config/openai_pricing.json
```

#### **UI-Based Updates**
- **Sidebar Section**: "💰 Pricing Management"
- **Refresh Button**: Reload from config file
- **Pricing Info**: Shows source and last update
- **Instructions**: Built-in update guidance

### 3. Enhanced Token Tracker
```python
# New methods in TokenTracker class
tracker.refresh_pricing()        # Reload pricing data
tracker.get_pricing_info()       # Get pricing metadata
```

## 📋 Usage Instructions

### For End Users
1. **View Current Pricing**: Check sidebar "Pricing Management" section
2. **Refresh Pricing**: Click "🔄 Refresh Pricing" button
3. **Update Instructions**: Expand "📝 Update Pricing" for guidance

### For Developers
1. **Manual Config Update**:
   ```json
   // Edit config/openai_pricing.json
   {
     "gpt-4": {"input": 0.03, "output": 0.06},
     "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
     "last_updated": "2025-07-28T12:00:00",
     "source": "manual_update"
   }
   ```

2. **Automated Script Update**:
   ```bash
   # Run the update script
   python update_pricing.py --method auto
   
   # Check what was updated
   cat config/openai_pricing.json
   ```

3. **Programmatic Update**:
   ```python
   from src.token_tracker import token_tracker
   
   # Refresh pricing in code
   if token_tracker.refresh_pricing():
       print("Pricing updated successfully")
   
   # Get pricing metadata
   info = token_tracker.get_pricing_info()
   print(f"Source: {info['pricing_source']}")
   ```

## 🔧 Available Update Methods

### 1. GitHub Community Repository
- **Pros**: Community-maintained, regularly updated
- **Cons**: Depends on community maintenance
- **Use Case**: Regular automated updates

### 2. Web Scraping OpenAI Website
- **Pros**: Direct from source, most accurate
- **Cons**: Fragile, may break with website changes
- **Use Case**: Verification of other sources

### 3. External Pricing APIs
- **Pros**: Reliable, structured data
- **Cons**: May not exist or require payment
- **Use Case**: Enterprise deployments

### 4. Manual Configuration
- **Pros**: Complete control, always works
- **Cons**: Requires manual effort
- **Use Case**: Custom pricing or testing

## 📊 Configuration File Format

```json
{
  "gpt-4": {
    "input": 0.03,
    "output": 0.06
  },
  "gpt-3.5-turbo": {
    "input": 0.0015,
    "output": 0.002
  },
  "last_updated": "2025-07-28T12:00:00Z",
  "source": "openai_website",
  "note": "Pricing per 1000 tokens in USD"
}
```

### Required Fields (per model):
- `input`: Cost per 1000 input tokens
- `output`: Cost per 1000 output tokens

### Optional Metadata:
- `last_updated`: ISO timestamp of last update
- `source`: Where pricing was obtained from
- `note`: Additional information

## 🚀 Best Practices

### 1. Regular Updates
- **Weekly Schedule**: Run `python update_pricing.py --method auto`
- **Monitor Changes**: Check `last_updated` field regularly
- **Version Control**: Commit pricing changes to track history

### 2. Validation
- **Test Updates**: Use `python test_pricing.py` after updates
- **Verify Costs**: Compare with OpenAI's official pricing page
- **Backup Config**: Keep backups of working configurations

### 3. Error Handling
- **Fallback Ready**: Always have working fallback pricing
- **Monitor Failures**: Log pricing update failures
- **Alert Systems**: Set up alerts for pricing update failures

## 🔍 Troubleshooting

### Common Issues:

1. **"Config file not found"**
   ```bash
   # Create initial config
   python update_pricing.py --method manual
   ```

2. **"Pricing refresh failed"**
   ```bash
   # Check config file format
   python -m json.tool config/openai_pricing.json
   ```

3. **"No external sources available"**
   ```bash
   # Use manual method
   python update_pricing.py --method manual
   # Edit config/openai_pricing.json
   ```

4. **"Outdated pricing warning"**
   ```bash
   # Update pricing
   python update_pricing.py --method auto
   ```

## 🎯 Future Enhancements

### Planned Features:
- **Automatic Scheduling**: Cron job for regular updates
- **Price Change Alerts**: Notify when prices change significantly
- **Historical Tracking**: Keep history of price changes
- **Model Auto-Discovery**: Detect new OpenAI models automatically
- **Cost Budgeting**: Set spending limits and alerts

### Integration Options:
- **CI/CD Pipeline**: Automated pricing updates in deployments
- **Monitoring Systems**: Integration with observability tools
- **Admin Dashboard**: Web interface for pricing management
- **API Endpoints**: RESTful API for pricing management

This dynamic pricing system ensures your AI Chatbot always has accurate, up-to-date OpenAI pricing without requiring code changes or redeployments.

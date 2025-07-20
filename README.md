# StarLabs Twitter Bot 2.1 🌟
A powerful pure Python Twitter automation tool with multithreading support and comprehensive statistics tracking.

## 📚 Documentation & Tutorials
> ### [📖 English Tutorial](https://star-labs.gitbook.io/star-labs/twitter/eng)
> ### [📖 Russian Tutorial](https://star-labs.gitbook.io/star-labs/twitter/ru)

## ✨ Features
- 📊 Real-time statistics display
- 🎨 Beautiful CLI interface with gradient display
- 🔄 Automatic retries with configurable attempts
- 🔧 Python-based configuration system
- 📝 JSON-based account management
- 🚀 Multiple account support with optional shuffle
- 📱 Telegram integration for reporting
- 🛠️ Wide range of Twitter actions:
  - Follow/Unfollow users
  - Like tweets
  - Retweet posts
  - Post tweets with/without images
  - Comment on tweets with/without images
  - Quote tweets with/without images
  - Account validation

## 📋 Requirements
- Python 3.11.6 or higher
- JSON storage for Twitter accounts
- Valid Twitter authentication tokens
- (Optional) Proxies for account management

## 🔧 Installation
1. Clone the repository:
```bash
git clone https://github.com/0xStarLabs/StarLabs-Twitter
cd StarLabs-Twitter
```

2. Run the setup script:
```bash
python setup.py install
```

3. Start the bot:
```bash
python setup.py start
# or
python main.py
```

## 🚀 Quick Start
1. Run the setup:
```bash
python setup.py install
```

2. Start the bot and follow the interactive setup:
```bash
python main.py
```

3. Use the menu to:
   - Add your Twitter accounts
   - Configure bot settings
   - Add tweet texts and images
   - Start farming

## 📁 Project Structure
```
StarLabs-Twitter/
├── data/
│   ├── accounts.json        # Twitter accounts data
│   ├── tweet_texts.json     # Tweets content
│   ├── comment_texts.json   # Comments for interactions
│   └── images/              # Images for media tweets
├── src/
│   ├── model/               # Core Twitter functionality
│   │   ├── twitter/         # Twitter API handlers
│   │   ├── instance.py      # Account instance management
│   │   ├── prepare_data.py  # Data preparation utilities
│   │   └── start.py         # Main execution flow
│   └── utils/               # Utility functions
│       ├── telegram_logger.py # Telegram integration
│       ├── reader.py        # Data readers (compatibility)
│       ├── output.py        # CLI output formatting
│       └── config.py        # Configuration compatibility
├── config.py                # Main configuration module
├── accounts_manager.py      # Account management
├── data_manager.py          # Text and image management
├── setup.py                 # Setup and installation
├── process.py               # Main process handler
└── main.py                  # Entry point
```

## 📝 Configuration

### 1. Account Setup
The bot now uses JSON storage for accounts. Use the interactive menu to:
- Add accounts with auth tokens and proxies
- View and manage existing accounts
- Remove accounts when needed

### 2. Configuration
All configuration is now done through Python. Use the interactive configuration menu to set:
- Number of threads
- Retry attempts
- Telegram notifications
- Tweet and comment settings

### 3. Content Management
Use the interactive menu to manage:
- **Tweet texts**: Add, view, and edit tweet content
- **Comment texts**: Add, view, and edit comment content
- **Images**: Place .jpg or .png images in the data/images/ folder

## 🚀 Usage
1. Run the setup and start the bot:
```bash
python main.py
```

2. Use the main menu to:
   - Manage accounts
   - Configure settings
   - Add content (tweets, comments, images)
   - Start farming

3. When farming, choose tasks to perform:
   - Follow
   - Like
   - Retweet
   - Comment
   - Comment with image
   - Tweet
   - Tweet with image
   - Quote
   - Quote with image
   - Unfollow
   - Check Valid
   - Exit

4. For each task, the bot will prompt for necessary input such as usernames or tweet URLs

## 📊 Statistics
The bot tracks detailed statistics for each run:
- Total accounts processed
- Success/failure rates by task
- Individual account results
- Task-specific performance metrics

Optional Telegram reporting can send detailed statistics at the end of execution.

## 🔧 Advanced Usage

### Command Line Setup
```bash
python setup.py install    # Full installation
python setup.py start      # Start the bot
```

## 🌐 Support
- GitHub: https://github.com/0xStarLabs
- Telegram: https://t.me/StarLabsTech
- Chat: https://t.me/StarLabsChat

## ⚠️ Disclaimer
This tool is for educational purposes only. Use at your own risk and in accordance with Twitter's Terms of Service.
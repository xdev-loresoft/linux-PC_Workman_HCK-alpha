# hck_GPT Module

## Description

hck_GPT is the AI assistant module for PC Workman, providing intelligent system optimizations and user support.

## Module Structure

```
hck_gpt/
├── __init__.py                  # Module initialization
├── chat_handler.py              # Main chat logic and command processing
├── service_setup_wizard.py      # Windows services optimization wizard
├── services_manager.py          # Windows services manager (enable/disable)
└── README.md                    # Documentation (this file)
```

## Features

### 1. Service Setup Wizard

Interactive wizard that helps users optimize their PC by disabling unnecessary Windows services.

**How to use:**
```
> service setup
```

**Process:**
1. Welcome and explanation
2. Series of questions about specific features (Printer, Bluetooth, Remote Desktop, etc.)
3. Summary and confirmation
4. Apply optimizations
5. Save configuration

**Questions asked by wizard:**
- Do you have a Printer connected to your PC?
- Do you use Bluetooth devices?
- Do you use Remote Desktop or PC sharing?
- Do you use Fax services?
- Do you have a drawing tablet or use pen input?
- Do you use Xbox gaming features?
- Do you want to keep Windows telemetry enabled?

### 2. Services Manager

Manages Windows services - disables and enables them based on user preferences.

**Supported service categories:**
- **Printer** - Print Spooler
- **Bluetooth** - Bluetooth Support Services
- **Remote** - Remote Desktop & Registry
- **Fax** - Fax Service
- **Tablet** - Tablet Input Service
- **Xbox** - Xbox Services (XblAuthManager, XblGameSave, etc.)
- **Telemetry** - Windows Telemetry & Diagnostics

**Configuration saved in:**
```
data/services_config.json
```

### 3. Chat Handler

Processes user messages and routes them to appropriate components.

**Available commands:**

| Command | Description |
|---------|-------------|
| `service setup` | Launch optimization wizard |
| `service status` | Show services status |
| `restore services` | Restore all disabled services |
| `help` | Show available commands |

## Integration

### In UI (hck_gpt_panel.py)

```python
from hck_gpt.chat_handler import ChatHandler

# Initialize
self.chat_handler = ChatHandler()

# Process messages
responses = self.chat_handler.process_message(user_input)
for response in responses:
    self.add_message(response)
```

## Example Flow

### Service Setup - Full Process

```
User: service setup

GPT: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     📋 Service Setup - Welcome!
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     Do you want to quick setup to disable
     useless services for your PC?

     E.g. Print Spooler, Bluetooth, Remote Desktop
     and more services that take system resources.

     Type 'Yes' to start or 'No' to cancel

User: yes

GPT: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     🔧 Service Setup [1/7]
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     Do you have a Printer connected to your PC?
     (Yes/No)

User: no

GPT: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     🔧 Service Setup [2/7]
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     Do you use Bluetooth devices?
     (Yes/No)

... (more questions)

GPT: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     ✅ Service Setup - Summary
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     Based on your answers, these services
     will be DISABLED to optimize your PC:

       • Print Spooler
       • Bluetooth Support
       • Fax Service

     Type 'Yes' to apply or 'No' to cancel

User: yes

GPT: ⚙️  Applying optimizations...
     ✅ Disabled: Print Spooler
     ✅ Disabled: Bluetooth Support
     ✅ Disabled: Fax Service

     ✨ Optimization Complete!
        3 services optimized
```

## Administrator Permissions

**IMPORTANT:** Managing Windows services requires administrator permissions.

To disable/enable services, the application must be run as administrator.

## Configuration

Configuration file: `data/services_config.json`

```json
{
  "disabled": [
    "Spooler",
    "bthserv",
    "BluetoothUserService"
  ],
  "timestamp": "2025-11-26 21:30:00"
}
```

## Development

### Adding New Service Category

In `services_manager.py`:

```python
SERVICES = {
    "new_category": {
        "services": ["ServiceName1", "ServiceName2"],
        "display": "Display Name",
        "description": "Service description"
    }
}
```

In `service_setup_wizard.py`:

```python
self.questions.append({
    "id": "new_category",
    "question": "Question for user?",
    "hint": "(Yes/No)",
    "service_category": "new_category"
})
```

### Adding New Command

In `chat_handler.py`:

```python
def process_message(self, user_message):
    # ...
    elif "new command" in message_lower:
        return self._handle_new_command()
```

## Debugging

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Features (Roadmap)

- Full AI integration (GPT/LLM)
- Real-time performance analysis
- Intelligent optimization suggestions
- Predictive monitoring
- Export/import configurations
- Optimization schedules
- Problem notifications

## License

Part of PC Workman - HCK_Labs  
Developed by Marcin "HCK" Firmuga

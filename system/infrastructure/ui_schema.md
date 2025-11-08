# UI-MD Schema: Pure Markdown UI Definition Format

## Overview

UI-MD (User Interface Markdown) is a declarative format for defining mobile application user interfaces within the LLMunix framework. It extends the "Pure Markdown" philosophy to UI generation, enabling LLM agents to create dynamic, personalized mobile experiences without requiring traditional app compilation.

## Design Philosophy

**Pure Markdown UI**: Everything is markdown with YAML frontmatter and custom component syntax
**Declarative**: Describes what the UI should be, not how to build it
**Composable**: Components can be nested and combined
**LLM-Friendly**: Easily generated and modified by language models
**Shell-Renderable**: Generic mobile shell apps can parse and render UI-MD in real-time

## Document Structure

```markdown
---
app_id: unique-app-identifier
user_id: user123
layout: vertical_stack | horizontal_stack | grid
theme: light | dark | auto
generated_at: ISO8601 timestamp
version: "1.0"
---

# App Title

<component> definitions...
```

## Core Component Types

### 1. Header Component

Displays prominent text at the top of the screen.

```markdown
<component type="Header">
  text: "Welcome to Your App"
  size: 24
  alignment: center | left | right
  color: "#FFFFFF"
</component>
```

**Parameters:**
- `text` (required): String to display
- `size` (optional): Font size in points (default: 20)
- `alignment` (optional): Text alignment (default: left)
- `color` (optional): Hex color code (default: theme primary)

### 2. Text Component

Standard text display with formatting options.

```markdown
<component type="Text">
  content: "Your content here"
  size: 16
  weight: normal | bold | light
  color: "#000000"
  markdown: true
</component>
```

**Parameters:**
- `content` (required): Text content (supports markdown if enabled)
- `size` (optional): Font size (default: 16)
- `weight` (optional): Font weight (default: normal)
- `color` (optional): Hex color code
- `markdown` (optional): Enable markdown rendering (default: false)

### 3. Card Component

Container for grouped information with optional actions.

```markdown
<component type="Card">
  title: "Card Title"
  content: |
    **Bold text**
    Regular text
    - List item
  action:
    id: "card_action_id"
    label: "Action Button"
  style: default | elevated | outlined
</component>
```

**Parameters:**
- `title` (optional): Card header text
- `content` (required): Main content (markdown supported)
- `action` (optional): Action button configuration
  - `id`: Unique action identifier
  - `label`: Button text
- `style` (optional): Visual style (default: default)

### 4. List Component

Displays a scrollable list of items.

```markdown
<component type="List">
  title: "List Title"
  items:
    - "Item 1"
    - "Item 2"
    - "Item 3"
  selectable: true
  action:
    id: "list_item_select"
</component>
```

**Parameters:**
- `title` (optional): List header
- `items` (required): Array of strings to display
- `selectable` (optional): Allow item selection (default: false)
- `action` (optional): Action triggered on item selection

### 5. Button Component

Interactive button for user actions.

```markdown
<component type="Button">
  label: "Click Me"
  action:
    id: "button_action_id"
    style: primary | secondary | danger
    params:
      key: value
  disabled: false
</component>
```

**Parameters:**
- `label` (required): Button text
- `action` (required): Action configuration
  - `id`: Action identifier sent to backend
  - `style`: Visual style (default: primary)
  - `params`: Optional key-value data
- `disabled` (optional): Disable interaction (default: false)

### 6. Input Component

Text input field for user data entry.

```markdown
<component type="Input">
  placeholder: "Enter text..."
  value: "Initial value"
  type: text | number | email | password
  action:
    id: "input_submit"
    trigger: submit | change
</component>
```

**Parameters:**
- `placeholder` (optional): Hint text
- `value` (optional): Initial value
- `type` (optional): Input type (default: text)
- `action` (required): Submit action configuration

### 7. Image Component

Display images from URLs or embedded data.

```markdown
<component type="Image">
  src: "https://example.com/image.png"
  alt: "Image description"
  width: 100%
  height: auto
  action:
    id: "image_tap"
</component>
```

**Parameters:**
- `src` (required): Image URL or data URI
- `alt` (optional): Accessibility description
- `width` (optional): Width (px or %) (default: 100%)
- `height` (optional): Height (default: auto)
- `action` (optional): Tap action

### 8. Grid Component

Layout components in a grid pattern.

```markdown
<component type="Grid">
  columns: 2
  spacing: 16
  items:
    - type: Card
      title: "Grid Item 1"
      content: "Content 1"
    - type: Card
      title: "Grid Item 2"
      content: "Content 2"
</component>
```

**Parameters:**
- `columns` (required): Number of columns
- `spacing` (optional): Gap between items in pixels
- `items` (required): Array of component definitions

### 9. Divider Component

Visual separator between sections.

```markdown
<component type="Divider">
  style: solid | dashed
  color: "#CCCCCC"
  thickness: 1
</component>
```

**Parameters:**
- `style` (optional): Line style (default: solid)
- `color` (optional): Line color
- `thickness` (optional): Line thickness in pixels

### 10. LoadingIndicator Component

Shows loading state during async operations.

```markdown
<component type="LoadingIndicator">
  text: "Loading data..."
  style: spinner | progress
</component>
```

**Parameters:**
- `text` (optional): Status message
- `style` (optional): Indicator type (default: spinner)

## Action System

Actions enable user interactions to trigger backend processing. When a user interacts with a component (tap, submit, etc.), the mobile shell sends the action to the LLMunix backend.

### Action Structure

```yaml
action:
  id: "unique_action_identifier"
  style: primary | secondary | danger
  trigger: tap | submit | change
  params:
    custom_key: custom_value
```

### Action Flow

1. **User Interaction**: User taps button with `action.id = "refresh_weather"`
2. **Shell Request**: Mobile app sends to backend:
   ```json
   {
     "app_id": "morning-briefing-user123",
     "user_id": "user123",
     "action_id": "refresh_weather",
     "params": {}
   }
   ```
3. **Backend Processing**: LLMunix `UIGeneratorAgent` handles the action
4. **UI Update**: Backend responds with updated UI-MD
5. **Shell Re-render**: Mobile app displays the new UI

## Example: Complete Morning Briefing App

```markdown
---
app_id: morning-briefing-user123
user_id: user123
layout: vertical_stack
theme: dark
generated_at: "2025-11-07T10:00:00Z"
version: "1.0"
---

# Morning Briefing for Alex

<component type="Header">
  text: "Good Morning, Alex! ☀️"
  size: 24
  alignment: center
</component>

<component type="Divider">
  style: solid
</component>

<component type="Card">
  title: "San Francisco Weather"
  content: |
    **Now:** 65°F, Sunny
    **High:** 72°F
    **Low:** 58°F

    Perfect day for a walk!
  action:
    id: "refresh_weather"
    label: "Refresh"
    style: secondary
</component>

<component type="Card">
  title: "Today's Calendar"
  content: |
    **09:00** - Team Sync (30 min)
    **11:00** - Project Deep Dive (1 hr)
    **14:30** - Dentist Appointment
</component>

<component type="List">
  title: "Top Tech News"
  items:
    - "GPT-5 rumors circulate after OpenAI teaser"
    - "Quantum computing breakthrough at Stanford"
    - "New React framework gains traction"
  selectable: true
  action:
    id: "open_news_article"
</component>

<component type="Button">
  label: "Add New Task"
  action:
    id: "show_add_task_form"
    style: primary
</component>

<component type="Text">
  content: "Last updated: 10:00 AM"
  size: 12
  color: "#888888"
</component>
```

## Design Guidelines for Agent Generators

### For UIGeneratorAgent

1. **Always query UserMemoryAgent first** to personalize content
2. **Use semantic component names** that describe function
3. **Provide meaningful action IDs** for backend routing
4. **Include refresh actions** for dynamic content
5. **Add loading states** during async operations
6. **Consider theme preferences** from user memory
7. **Structure content hierarchically** (header → cards → lists → actions)

### Performance Considerations

- **Minimize component nesting** for faster rendering
- **Lazy load images** with placeholder states
- **Batch actions** when possible
- **Cache static content** between updates

### Accessibility

- Always include `alt` text for images
- Use semantic component hierarchy
- Ensure sufficient color contrast
- Provide text alternatives for icons

## Version History

- **v1.0** (2025-11-07): Initial UI-MD schema definition for LLMunix Wabi POC

## Related Components

- **UIGeneratorAgent** (`system/agents/UIGeneratorAgent.md`): Generates UI-MD files
- **UserMemoryAgent** (`system/agents/UserMemoryAgent.md`): Provides personalization data
- **Mobile Shell App**: Parses and renders UI-MD (external React Native/Flutter app)

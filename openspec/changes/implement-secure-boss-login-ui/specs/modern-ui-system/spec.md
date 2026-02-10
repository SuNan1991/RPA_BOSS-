# Capability: Modern UI System

现代化 UI 系统能力。提供极简、玻璃拟态风格的设计组件库。

## ADDED Requirements

### Requirement: Configure Tailwind CSS with custom theme

The system SHALL configure Tailwind CSS with custom theme settings including primary color #5C6BC0.

#### Scenario: Initialize Tailwind CSS configuration
- **WHEN** developer sets up Tailwind CSS
- **THEN** system creates `tailwind.config.js` file
- **AND** configures `content` paths to scan all Vue files
- **AND** sets `darkMode: 'class'` to enable manual theme switching
- **AND** extends theme with custom colors:
  - `primary: #5C6BC0`
  - `primary-light: #7E8CD8`
  - `primary-dark: #3F51B5`
- **AND** configures custom font family (Inter or system fonts)
- **AND** configures custom spacing scale for consistent layout

#### Scenario: Configure Tailwind plugins
- **WHEN** Tailwind CSS is initialized
- **THEN** system includes `@tailwindcss/forms` plugin for better form styling
- **AND** includes `@tailwindcss/typography` plugin for prose content
- **AND** configures plugin options if needed

#### Scenario: Generate Tailwind CSS build
- **WHEN** developer runs `npm run dev` or `npm run build`
- **THEN** Tailwind scans all Vue files for class names
- **AND** generates CSS file with only used utilities
- **AND** outputs CSS file to `dist/assets/index.xxx.css`
- **AND** CSS file size is < 50KB for production build

### Requirement: Implement CSS Variables for dynamic theming

The system SHALL use CSS Variables for dynamic theme switching and color customization.

#### Scenario: Define CSS Variables for colors
- **WHEN** system initializes theme
- **THEN** system defines CSS variables in `:root` selector:
  - `--primary: #5C6BC0`
  - `--primary-light: #7E8CD8`
  - `--primary-dark: #3F51B5`
  - `--glass-bg: rgba(255, 255, 255, 0.7)`
  - `--glass-border: rgba(255, 255, 255, 0.18)`
  - `--text-primary: #1a1a1a`
  - `--text-secondary: #666666`
  - `--bg-primary: #f5f5f5`
  - `--bg-secondary: #ffffff`

#### Scenario: Override CSS Variables for dark mode
- **WHEN** dark mode is activated
- **THEN** system overrides CSS variables in `.dark` selector:
  - `--primary: #7E8CD8` (lighter for dark mode)
  - `--glass-bg: rgba(0, 0, 0, 0.7)`
  - `--glass-border: rgba(255, 255, 255, 0.08)`
  - `--text-primary: #f5f5f5`
  - `--text-secondary: #a0a0a0`
  - `--bg-primary: #121212`
  - `--bg-secondary: #1a1a1a`

#### Scenario: Reference CSS Variables in Tailwind config
- **WHEN** Tailwind CSS is configured
- **THEN** system references CSS variables in `tailwind.config.js`:
  ```javascript
  colors: {
    primary: 'var(--primary)',
    'primary-light': 'var(--primary-light)',
    'primary-dark': 'var(--primary-dark)',
    glass: 'var(--glass-bg)',
  }
  ```
- **AND** allows dynamic theme switching without rebuild

### Requirement: Implement glassmorphism utility classes

The system SHALL provide utility classes for glassmorphism effect with backdrop blur.

#### Scenario: Create base glassmorphism utility class
- **WHEN** developer applies `.glass` class to an element
- **THEN** element has background color using CSS variable `--glass-bg`
- **AND** applies `backdrop-filter: blur(20px)`
- **AND** applies `-webkit-backdrop-filter: blur(20px)` for Safari support
- **AND** adds border using `--glass-border` CSS variable
- **AND** adds subtle box-shadow: `0 8px 32px 0 rgba(31, 38, 135, 0.37)`

#### Scenario: Create glassmorphism variant classes
- **WHEN** developer applies `.glass-light` class
- **THEN** element uses lighter glass effect (more transparent, less blur)
- **AND** background uses `rgba(255, 255, 255, 0.5)` in light mode
- **AND** backdrop-filter uses `blur(10px)`

#### Scenario: Create glassmorphism card variant
- **WHEN** developer applies `.glass-card` class
- **THEN** element combines glass effect with card styling
- **AND** adds rounded corners (`rounded-2xl` or `border-radius: 1rem`)
- **AND** adds padding (`p-6` or `padding: 1.5rem`)
- **AND** adds subtle border and shadow

#### Scenario: Fallback for browsers without backdrop-filter support
- **WHEN** browser does not support backdrop-filter
- **THEN** system uses `@supports not (backdrop-filter: blur(20px))` query
- **AND** applies fallback solid background color with higher opacity
- **AND** maintains visual consistency as much as possible

### Requirement: Implement responsive breakpoint system

The system SHALL use Tailwind's responsive breakpoint system for adaptive layout.

#### Scenario: Define custom breakpoints
- **WHEN** Tailwind CSS is configured
- **THEN** system defines breakpoints:
  - `sm: 640px` (small mobile)
  - `md: 768px` (tablet)
  - `lg: 1024px` (desktop)
  - `xl: 1280px` (large desktop)
  - `2xl: 1536px` (extra large desktop)

#### Scenario: Apply responsive utility classes
- **WHEN** developer uses responsive utilities (e.g., `w-full md:w-1/2 lg:w-1/3`)
- **THEN** element width changes based on viewport size
- **AND** mobile (< 768px): element is full width
- **AND** tablet (768px - 1024px): element is half width
- **AND** desktop (> 1024px): element is one-third width

#### Scenario: Mobile-first responsive design
- **WHEN** developer writes responsive styles
- **THEN** system uses mobile-first approach (base styles for mobile, add breakpoints for larger screens)
- **AND** example: `p-4 md:p-8 lg:p-12` (padding increases with screen size)

### Requirement: Implement dark mode toggle mechanism

The system SHALL provide a mechanism to toggle between light and dark modes.

#### Scenario: Add dark mode class to HTML element
- **WHEN** user toggles to dark mode
- **THEN** system adds `.dark` class to `<html>` or `<body>` element
- **AND** all Tailwind `dark:` prefixed utilities become active
- **AND** all CSS Variables are overridden to dark mode values

#### Scenario: Remove dark mode class for light mode
- **WHEN** user toggles to light mode
- **THEN** system removes `.dark` class from HTML element
- **AND** all Tailwind `dark:` utilities become inactive
- **AND** CSS Variables revert to light mode values

#### Scenario: Persist theme preference to localStorage
- **WHEN** user toggles theme
- **THEN** system saves theme preference to `localStorage.getItem('theme')`
- **AND** saves value `'light'` or `'dark'`
- **AND** on next page load, system reads from localStorage
- **AND** applies saved theme before rendering (no flash of wrong theme)

#### Scenario: Detect system theme preference
- **WHEN** user visits application for the first time (no localStorage preference)
- **THEN** system uses `window.matchMedia('(prefers-color-scheme: dark)')`
- **AND** applies dark mode if system prefers dark
- **AND** applies light mode if system prefers light
- **AND** saves detected preference to localStorage

### Requirement: Implement smooth transitions and animations

The system SHALL provide smooth transitions and animations for better user experience.

#### Scenario: Add transition utility classes
- **WHEN** developer applies `.transition-all` class
- **THEN** element animates all CSS property changes
- **AND** transition duration is 300ms by default
- **AND** transition timing function is `ease-in-out`
- **AND** example: hover effect on button has smooth color transition

#### Scenario: Add custom animation utilities
- **WHEN** developer applies animation classes (`.animate-spin`, `.animate-pulse`, `.animate-bounce`)
- **THEN** element plays predefined Tailwind animations
- **AND** `.animate-spin`: rotates 360 degrees continuously
- **AND** `.animate-pulse`: fades in and out continuously
- **AND** `.animate-bounce`: bounces up and down

#### Scenario: Create custom animation in Tailwind config
- **WHEN** developer needs custom animation
- **THEN** system defines animation in `tailwind.config.js`:
  ```javascript
  keyframes: {
    'fade-in': {
      '0%': { opacity: '0' },
      '100%': { opacity: '1' },
    },
  }
  ```
- **AND** developer can use `.animate-fade-in` class

#### Scenario: Smooth theme transition
- **WHEN** user toggles theme
- **THEN** system applies transition to background and color changes
- **AND** transition duration is 300ms
- **AND** theme switch is smooth, not abrupt

### Requirement: Implement typography system

The system SHALL provide consistent typography using Tailwind's typography utilities.

#### Scenario: Define font family
- **WHEN** Tailwind CSS is configured
- **THEN** system sets font family to:
  - `font-sans`: Inter, system-ui, -apple-system, sans-serif
  - `font-mono`: 'Fira Code', 'Courier New', monospace
- **AND** fonts are loaded from CDN or bundled with application

#### Scenario: Use typography scale
- **WHEN** developer applies text size utilities (`.text-xs`, `.text-sm`, `.text-base`, `.text-lg`, `.text-xl`, `.text-2xl`)
- **THEN** font sizes follow consistent scale:
  - `text-xs`: 0.75rem (12px)
  - `text-sm`: 0.875rem (14px)
  - `text-base`: 1rem (16px)
  - `text-lg`: 1.125rem (18px)
  - `text-xl`: 1.25rem (20px)
  - `text-2xl`: 1.5rem (24px)

#### Scenario: Apply font weights
- **WHEN** developer applies font weight utilities (`.font-light`, `.font-normal`, `.font-medium`, `.font-bold`)
- **THEN** font weights follow:
  - `font-light`: 300
  - `font-normal`: 400
  - `font-medium`: 500
  - `font-bold`: 700

#### Scenario: Responsive typography
- **WHEN** developer uses responsive text utilities (e.g., `.text-sm md:text-base lg:text-lg`)
- **THEN** text size increases with screen size
- **AND** ensures readability on all devices

### Requirement: Implement spacing system

The system SHALL use Tailwind's consistent spacing scale for layout and padding.

#### Scenario: Use spacing scale
- **WHEN** developer applies spacing utilities (`.p-4`, `.m-4`, `.gap-4`)
- **THEN** spacing values follow consistent scale:
  - `0`: 0
  - `1`: 0.25rem (4px)
  - `2`: 0.5rem (8px)
  - `3`: 0.75rem (12px)
  - `4`: 1rem (16px)
  - `5`: 1.25rem (20px)
  - `6`: 1.5rem (24px)
  - `8`: 2rem (32px)
  - `10`: 2.5rem (40px)
  - `12`: 3rem (48px)

#### Scenario: Container with max-width
- **WHEN** developer applies `.container` class
- **THEN** element has max-width based on breakpoint:
  - `sm`: 640px
  - `md`: 768px
  - `lg`: 1024px
  - `xl`: 1280px
  - `2xl`: 1536px
- **AND** element is centered horizontally with `mx-auto`

#### Scenario: Consistent padding for sections
- **WHEN** developer creates layout sections
- **THEN** system uses consistent padding: `.py-12 md:py-16 lg:py-20`
- **AND** vertical padding increases with screen size

### Requirement: Implement focus and accessibility states

The system SHALL provide clear focus states for keyboard navigation and accessibility.

#### Scenario: Focus ring on interactive elements
- **WHEN** user navigates using keyboard (Tab key)
- **THEN** interactive elements (buttons, links, inputs) show focus ring
- **AND** focus ring uses primary color #5C6BC0
- **AND** focus ring is 2px solid outline
- **AND** focus ring has offset of 2px from element

#### Scenario: Focus visible only for keyboard navigation
- **WHEN** user clicks element with mouse
- **THEN** focus ring is NOT shown (only show for keyboard navigation)
- **AND** system uses `:focus-visible` pseudo-class (not `:focus`)

#### Scenario: High contrast mode support
- **WHEN** user has high contrast mode enabled in OS
- **THEN** system respects high contrast mode settings
- **AND** adjusts colors to meet WCAG AAA contrast requirements
- **AND** uses `@media (prefers-contrast: high)` media query

### Requirement: Implement loading and skeleton states

The system SHALL provide loading states and skeleton screens for better perceived performance.

#### Scenario: Spinner loading indicator
- **WHEN** async operation is in progress
- **THEN** system displays spinner animation
- **AND** spinner uses primary color #5C6BC0
- **AND** spinner is centered in container
- **AND** spinner size is appropriate (32px or 48px)

#### Scenario: Skeleton screen for content loading
- **WHEN** content is loading (e.g., user information)
- **THEN** system displays skeleton placeholder
- **AND** skeleton has gray background with animated shimmer effect
- **AND** skeleton matches shape of content (e.g., circle for avatar, rectangle for text)
- **AND** skeleton animation uses `animate-pulse` class

#### Scenario: Button loading state
- **WHEN** button is clicked and async operation starts
- **THEN** button shows spinner icon
- **AND** button text changes to loading message (e.g., "加载中...")
- **AND** button is disabled during loading
- **AND** button maintains same width to prevent layout shift

### Requirement: Implement toast/notification system

The system SHALL provide toast notifications for user feedback (success, error, warning, info).

#### Scenario: Display success toast
- **WHEN** operation completes successfully
- **THEN** system displays toast notification with:
  - Green background or green icon
  - Success message text
  - Auto-dismiss after 5 seconds
  - Dismiss button (X icon)
- **AND** toast slides in from top-right corner
- **AND** toast uses glassmorphism effect

#### Scenario: Display error toast
- **WHEN** operation fails
- **THEN** system displays toast notification with:
  - Red background or red icon
  - Error message text
  - No auto-dismiss (user must dismiss manually)
  - Dismiss button (X icon)
- **AND** toast slides in from top-right corner

#### Scenario: Multiple toasts stacking
- **WHEN** multiple toasts are triggered
- **THEN** toasts stack vertically on top of each other
- **AND** newest toast appears on top
- **AND** maximum 3 toasts visible at once (older toasts auto-dismiss)

#### Scenario: Toast positioning in mobile
- **WHEN** system is in mobile view (< 768px)
- **THEN** toasts appear at bottom of screen (not top-right)
- **AND** toasts are full-width with padding on sides

### Requirement: Implement button component variants

The system SHALL provide button component with multiple variants (primary, secondary, ghost, danger).

#### Scenario: Primary button
- **WHEN** developer uses `.btn-primary` class
- **THEN** button has:
  - Background color: #5C6BC0
  - Text color: white
  - Rounded corners: `rounded-lg` (8px)
  - Padding: `px-6 py-3` (horizontal: 24px, vertical: 12px)
  - Font weight: `font-medium`
  - Hover state: darker background (#3F51B5)
  - Active state: even darker background (#303F9F)

#### Scenario: Secondary button
- **WHEN** developer uses `.btn-secondary` class
- **THEN** button has:
  - Background color: transparent
  - Border: 1px solid #5C6BC0
  - Text color: #5C6BC0
  - Hover state: background color with low opacity (rgba(92, 107, 192, 0.1))

#### Scenario: Ghost button
- **WHEN** developer uses `.btn-ghost` class
- **THEN** button has:
  - Background color: transparent
  - Text color: #5C6BC0
  - Hover state: background color with very low opacity (rgba(92, 107, 192, 0.05))
  - No border

#### Scenario: Danger button
- **WHEN** developer uses `.btn-danger` class
- **THEN** button has:
  - Background color: red (#EF4444)
  - Text color: white
  - Hover state: darker red (#DC2626)
  - Used for destructive actions (logout, delete)

### Requirement: Implement form input component styles

The system SHALL provide consistent form input styles with focus and validation states.

#### Scenario: Text input field
- **WHEN** developer uses `.input` class
- **THEN** input has:
  - Border: 1px solid #e5e7eb
  - Rounded corners: `rounded-md` (6px)
  - Padding: `px-4 py-2`
  - Font size: `text-base`
  - Background color: white (or dark gray in dark mode)
  - Focus state: border color changes to #5C6BC0
  - Focus state: box-shadow with primary color

#### Scenario: Input validation states
- **WHEN** input has validation error
- **THEN** input shows:
  - Red border color
  - Red error message text below input
  - Error icon (if applicable)
- **WHEN** input validation passes
- **THEN** input shows:
  - Green border color
  - Success icon (checkmark)

#### Scenario: Disabled input state
- **WHEN** input has `disabled` attribute
- **THEN** input shows:
  - Gray background color
  - Gray text color
  - Not interactive (no hover state)
  - Cursor: not-allowed

### Requirement: Ensure WCAG AA accessibility compliance

The system SHALL meet WCAG AA accessibility standards for color contrast and keyboard navigation.

#### Scenario: Color contrast ratio for text
- **WHEN** system displays text on background
- **THEN** contrast ratio is at least 4.5:1 for normal text
- **AND** contrast ratio is at least 3:1 for large text (18px+)
- **AND** contrast ratio is at least 3:1 for UI components (buttons, borders)

#### Scenario: Keyboard navigation
- **WHEN** user navigates using keyboard (Tab, Shift+Tab, Arrow keys)
- **THEN** all interactive elements are focusable
- **AND** focus order is logical (top to bottom, left to right)
- **AND** focus trap is implemented for modals (Tab cycles within modal)

#### Scenario: Screen reader support
- **WHEN** screen reader is used
- **THEN** all images have alt text
- **AND** all form inputs have labels
- **AND** all icons have aria-label or aria-hidden="true"
- **AND** semantic HTML is used (nav, main, section, h1-h6)

#### Scenario: Touch target size
- **WHEN** system displays on mobile device
- **THEN** all interactive elements have minimum touch target size of 44x44 pixels
- **AND** buttons and links are easily tappable
- **AND** spacing between clickable elements is sufficient

### Requirement: Optimize for performance

The system SHALL optimize CSS and assets for fast loading and rendering.

#### Scenario: Purge unused Tailwind CSS
- **WHEN** production build is created
- **THEN** Tailwind removes all unused utility classes
- **AND** CSS file size is minimized (< 50KB)
- **AND** only used classes are included in output

#### Scenario: Lazy load component styles
- **WHEN** component is not initially visible
- **THEN** component styles are loaded on-demand
- **AND** reduces initial CSS bundle size
- **AND** improves First Contentful Paint (FCP) metric

#### Scenario: CSS minification
- **WHEN** production build is created
- **THEN** CSS is minified (whitespace removed, comments removed)
- **AND** CSS is compressed with gzip or brotli
- **AND** browser receives minimal CSS payload

#### Scenario: Avoid layout shift
- **WHEN** page loads or updates
- **THEN** system reserves space for dynamic content (skeleton screens)
- **AND** uses `aspect-ratio` for images and videos
- **AND** avoids layout shift (Cumulative Layout Shift < 0.1)

# SPEC-CAL-004: Booking Widgets

**Module**: Calendars & Bookings
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-02-07
**Dependencies**: SPEC-CAL-001 (Calendar Management), SPEC-CAL-002 (Appointments), SPEC-CAL-003 (Availability)

---

## Executive Summary

Implement embeddable booking widgets that businesses can add to their websites, allowing customers to self-schedule appointments. Widgets support full customization including branding, colors, and confirmation flows, with responsive design for all devices.

---

## Business Context

### Problem Statement
Businesses need to provide easy booking options on their websites without redirecting customers to external platforms. Embeddable booking widgets reduce friction, increase conversion rates, and provide a seamless branded experience. Without customizable widgets, businesses cannot match their brand identity or control the booking experience.

### Goals
- Provide embeddable JavaScript widgets for easy website integration
- Enable full widget customization (branding, colors, layout)
- Support multiple widget types (inline, popup, full-page)
- Ensure responsive design for mobile and desktop
- Optimize booking flow for high conversion rates

---

## Requirements (EARS Format)

### 1. Widget Types and Embedding

**WHEN** a business adds a booking widget to their website, the system SHALL support three widget types:
- Inline widget: Embedded in page content
- Popup widget: Triggered by button click
- Full-page widget: Dedicated booking page

**WHILE** embedding widgets, the system SHALL provide:
- JavaScript snippet for copy-paste integration
- Simple HTML tag for basic integration
- React component for Next.js/React sites
- WordPress plugin for WordPress sites

**WHERE** widget is loaded, the system SHALL asynchronously load widget assets to avoid blocking page rendering.

**WHEN** widget initializes, it SHALL authenticate using calendar's public API key.

**IF** widget fails to load, it SHALL display graceful fallback message with link to booking page.

### 2. Widget Customization

**WHEN** configuring widget appearance, the system SHALL allow customization of:
- Primary and secondary colors
- Font family and sizes
- Border radius and spacing
- Logo and background image
- Welcome message and instructions

**WHILE** applying customizations, the system SHALL:
- Provide live preview of changes
- Generate CSS that doesn't conflict with host page
- Use scoped styles with CSS-in-JS or iframe isolation
- Respect dark/light mode preferences

**WHERE** no customization is applied, the system SHALL use calendar's default branding.

**WHEN** widget is embedded, customizations SHALL be applied instantly without requiring host site updates.

**IF** customization values are invalid (e.g., malformed color), the system SHALL revert to defaults and log warning.

### 3. Booking Flow

**WHEN** customer interacts with widget, the system SHALL guide them through:
1. Select service/appointment type
2. Choose date and time from available slots
3. Enter customer information (name, email, phone)
4. Confirm booking details
5. Receive confirmation

**WHILE** progressing through flow, the system SHALL:
- Save progress locally (continue if page refresh)
- Validate each step before proceeding
- Show clear error messages
- Display estimated completion time

**WHERE** calendar requires payment, the system SHALL integrate payment step before confirmation.

**WHEN** booking is confirmed, the system SHALL:
- Show success message with appointment details
- Send confirmation email
- Offer "Add to Calendar" download
- Display next steps (e.g., "Check your email")

**IF** booking fails, the system SHALL show helpful error and offer retry or alternative slots.

### 4. Responsive Design

**WHEN** widget loads on mobile devices, the system SHALL:
- Optimize touch targets (minimum 44x44px)
- Use full-width layout on small screens
- Enable swipe gestures for date selection
- Load mobile-optimized images

**WHILE** rendering on tablet, the system SHALL adapt layout for touch and pointer input.

**WHERE** widget loads on desktop, the system SHALL optimize for mouse interaction and keyboard navigation.

**WHEN** device orientation changes, the system SHALL smoothly adjust layout.

**IF** screen width is below 320px, the system SHALL display message to view on larger screen.

### 5. Widget Performance

**WHEN** widget loads, initial render SHALL complete in < 2 seconds on 3G connection.

**WHILE** navigating booking flow, each step transition SHALL complete in < 300ms.

**WHERE** widget retrieves availability, data SHALL be cached locally for 5 minutes.

**WHEN** widget is idle, it SHALL use < 50MB memory.

**IF** widget takes > 5 seconds to load, it SHALL display loading indicator and retry.

### 6. Privacy and Data Handling

**WHEN** customer enters information, the system SHALL:
- Collect only required fields
- Encrypt data in transit (HTTPS)
- Not store data on host page
- Submit directly to backend (bypass host site)

**WHILE** processing booking, customer data SHALL NOT be exposed to host website JavaScript.

**WHERE** widget is embedded on HTTP site, the system SHALL display security warning and redirect to HTTPS booking page.

**WHEN** booking completes, the system SHALL clear any temporary customer data from widget memory.

**IF** calendar is deleted or disabled, widget SHALL display "Booking unavailable" message.

### 7. Analytics and Tracking

**WHEN** widget loads, the system SHALL track:
- Page view (widget loaded)
- Widget type and calendar ID
- Referrer URL
- Device type and browser

**WHILE** customer interacts, the system SHALL track:
- Step completion rates (funnel analytics)
- Drop-off points
- Time spent per step
- Selected time slots

**WHERE** booking completes, the system SHALL track:
- Conversion rate
- Revenue (if payment required)
- Customer source (widget ID)

**WHEN** widget events occur, the system SHALL send analytics data to backend asynchronously.

**IF** analytics tracking fails, widget SHALL continue functioning without interruption.

---

## Domain Entities

### BookingWidget

```python
class BookingWidget:
    id: UUID
    calendar_id: UUID
    name: str
    widget_type: WidgetType  # inline, popup, full_page
    status: WidgetStatus  # active, inactive, archived

    # Customization
    primary_color: str  # Hex color
    secondary_color: str
    background_color: str
    text_color: str
    font_family: str
    border_radius: int  # pixels
    logo_url: Optional[str]
    background_image_url: Optional[str]
    welcome_message: str

    # Behavior
    require_payment: bool
    collect_customer_address: bool
    collect_customer_notes: bool
    allow_rescheduling: bool
    show_calendar_owner_photo: bool

    # Integration
    allowed_domains: List[str]  # Empty = allow all
    redirect_url: Optional[str]  # Post-booking redirect
    webhook_url: Optional[str]  # Booking notifications

    # Analytics
    track_conversions: bool
    tracking_id: Optional[str]  # Google Analytics, etc.

    # Metadata
    public_api_key: str  # For widget authentication
    created_at: datetime
    updated_at: datetime

    class WidgetType(Enum):
        INLINE = "inline"
        POPUP = "popup"
        FULL_PAGE = "full_page"

    class WidgetStatus(Enum):
        ACTIVE = "active"
        INACTIVE = "inactive"
        ARCHIVED = "archived"
```

### WidgetAnalytics

```python
class WidgetAnalytics:
    id: UUID
    widget_id: UUID
    event_type: AnalyticsEventType  # view, step_start, step_complete, booking, error
    timestamp: datetime

    # Context
    referrer_url: Optional[str]
    user_agent: str
    device_type: str  # mobile, tablet, desktop
    browser: str

    # Event data
    step_name: Optional[str]  # For step events
    time_spent_seconds: Optional[int]
    error_message: Optional[str]

    # Booking data (for booking events)
    appointment_id: Optional[UUID]
    booking_value: Optional[Decimal]

    class AnalyticsEventType(Enum):
        VIEW = "view"
        STEP_START = "step_start"
        STEP_COMPLETE = "step_complete"
        BOOKING = "booking"
        ERROR = "error"
```

### WidgetEmbed

```python
class WidgetEmbed:
    id: UUID
    widget_id: UUID
    domain: str  # Domain where widget is embedded
    embed_url: str
    page_path: Optional[str]
    first_seen_at: datetime
    last_seen_at: datetime
    is_active: bool
```

---

## API Design

### Widget Management

#### POST /api/v1/widgets
Create booking widget.

**Request:**
```json
{
  "calendar_id": "uuid",
  "name": "Website Booking Widget",
  "widget_type": "inline",
  "primary_color": "#3B82F6",
  "secondary_color": "#1E40AF",
  "welcome_message": "Schedule your consultation",
  "require_payment": false,
  "collect_customer_notes": true
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "public_api_key": "pk_...",
  "embed_code": {
    "javascript": "<script src=\"https://booking.example.com/widget.js\" data-calendar-id=\"uuid\"></script>",
    "react": "<BookingWidget calendarId=\"uuid\" />",
    "html": "<div id=\"booking-widget-uuid\"></div>"
  },
  "preview_url": "https://booking.example.com/preview/uuid"
}
```

#### GET /api/v1/widgets
List widgets for current user/organization.

#### GET /api/v1/widgets/{widget_id}
Get widget details and configuration.

#### PUT /api/v1/widgets/{widget_id}
Update widget configuration.

**Request:** Partial update allowed (only provided fields are updated).

**Response:** 200 OK with updated widget.

#### DELETE /api/v1/widgets/{widget_id}
Soft-delete widget (sets status to archived).

### Widget Public API

#### GET /api/v1/public/widgets/{public_api_key}
Get widget configuration (no authentication required).

**Response:** 200 OK
```json
{
  "id": "uuid",
  "calendar_id": "uuid",
  "widget_type": "inline",
  "primary_color": "#3B82F6",
  "welcome_message": "Schedule your consultation",
  "require_payment": false,
  "calendar_name": "Sales Consultations",
  "appointment_types": ["consultation", "demo", "support"]
}
```

#### GET /api/v1/public/widgets/{public_api_key}/availability
Get availability for widget (no authentication, rate-limited).

**Query Params:**
- `start_date`: Start date
- `end_date`: End date
- `timezone`: Timezone for display

**Response:** 200 OK (same format as appointments availability API).

#### POST /api/v1/public/widgets/{public_api_key}/book
Create appointment via widget (no authentication, rate-limited, CAPTCHA protected).

**Request:**
```json
{
  "slot_id": "uuid",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "notes": "Looking for consultation",
  "captcha_token": "recaptcha_token"
}
```

**Response:** 201 Created (appointment details).

### Widget Analytics

#### GET /api/v1/widgets/{widget_id}/analytics
Get widget analytics.

**Query Params:**
- `start_date`: Start date
- `end_date`: End date
- `event_type`: Filter by event type

**Response:** 200 OK
```json
{
  "total_views": 1500,
  "unique_visitors": 1200,
  "bookings": 150,
  "conversion_rate": 0.125,
  "drop_off_rate_by_step": {
    "service_selection": 0.10,
    "date_selection": 0.15,
    "customer_info": 0.05,
    "confirmation": 0.02
  },
  "top_referring_domains": [
    {"domain": "example.com", "views": 800, "bookings": 100}
  ],
  "device_breakdown": {
    "mobile": 900,
    "tablet": 300,
    "desktop": 300
  }
}
```

#### GET /api/v1/widgets/{widget_id}/embeds
List domains where widget is embedded.

---

## Database Schema

```sql
-- Booking widgets
CREATE TABLE booking_widgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_id UUID NOT NULL REFERENCES calendars(id),
    name VARCHAR(255) NOT NULL,
    widget_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    -- Customization
    primary_color VARCHAR(7) NOT NULL DEFAULT '#3B82F6',
    secondary_color VARCHAR(7) NOT NULL DEFAULT '#1E40AF',
    background_color VARCHAR(7) NOT NULL DEFAULT '#FFFFFF',
    text_color VARCHAR(7) NOT NULL DEFAULT '#000000',
    font_family VARCHAR(100) NOT NULL DEFAULT 'system-ui',
    border_radius INT NOT NULL DEFAULT 8,
    logo_url TEXT,
    background_image_url TEXT,
    welcome_message TEXT NOT NULL DEFAULT 'Book your appointment',

    -- Behavior
    require_payment BOOLEAN NOT NULL DEFAULT false,
    collect_customer_address BOOLEAN NOT NULL DEFAULT false,
    collect_customer_notes BOOLEAN NOT NULL DEFAULT true,
    allow_rescheduling BOOLEAN NOT NULL DEFAULT true,
    show_calendar_owner_photo BOOLEAN NOT NULL DEFAULT false,

    -- Integration
    allowed_domains JSONB,  -- Array of strings
    redirect_url TEXT,
    webhook_url TEXT,

    -- Analytics
    track_conversions BOOLEAN NOT NULL DEFAULT true,
    tracking_id VARCHAR(255),

    -- Authentication
    public_api_key VARCHAR(255) UNIQUE NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_widget_type CHECK (widget_type IN ('inline', 'popup', 'full_page')),
    CONSTRAINT valid_widget_status CHECK (status IN ('active', 'inactive', 'archived')),
    CONSTRAINT valid_color CHECK (primary_color ~* '^#[0-9A-F]{6}$')
);

CREATE INDEX idx_widgets_calendar ON booking_widgets(calendar_id);
CREATE INDEX idx_widgets_status ON booking_widgets(status) WHERE status = 'active';
CREATE INDEX idx_widgets_public_key ON booking_widgets(public_api_key);

-- Widget analytics
CREATE TABLE widget_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    widget_id UUID NOT NULL REFERENCES booking_widgets(id) ON DELETE CASCADE,
    event_type VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Context
    referrer_url TEXT,
    user_agent TEXT,
    device_type VARCHAR(20),
    browser VARCHAR(50),

    -- Event data
    step_name VARCHAR(100),
    time_spent_seconds INT,
    error_message TEXT,

    -- Booking data
    appointment_id UUID REFERENCES appointments(id),
    booking_value DECIMAL(10, 2),

    CONSTRAINT valid_event_type CHECK (event_type IN ('view', 'step_start', 'step_complete', 'booking', 'error'))
);

CREATE INDEX idx_widget_analytics_widget ON widget_analytics(widget_id);
CREATE INDEX idx_widget_analytics_timestamp ON widget_analytics(timestamp DESC);
CREATE INDEX idx_widget_analytics_event_type ON widget_analytics(event_type);

-- Widget embeds
CREATE TABLE widget_embeds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    widget_id UUID NOT NULL REFERENCES booking_widgets(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    embed_url TEXT NOT NULL,
    page_path TEXT,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX idx_embeds_widget ON widget_embeds(widget_id);
CREATE INDEX idx_embeds_domain ON widget_embeds(domain);
CREATE INDEX idx_embeds_active ON widget_embeds(is_active) WHERE is_active = true;
```

---

## Acceptance Criteria

### AC1: Widget Embedding
- GIVEN a business wants to add booking to website
- WHEN they copy JavaScript snippet and paste into HTML
- THEN widget loads and displays booking interface
- AND widget is fully functional
- AND does not break host page styling

### AC2: Widget Customization
- GIVEN widget with custom branding colors
- WHEN customer views widget
- THEN colors match customization exactly
- AND fonts and spacing are applied
- AND logo appears if configured

### AC3: Booking Flow Completion
- GIVEN customer using widget to book
- WHEN they complete all steps
- THEN appointment is created
- AND confirmation email is sent
- AND success message displays
- AND "Add to Calendar" link works

### AC4: Mobile Responsiveness
- GIVEN widget loaded on mobile phone
- WHEN customer interacts with booking flow
- THEN all elements are touch-friendly
- AND layout adapts to portrait/landscape
- AND text is readable without zooming

### AC5: Performance Standards
- GIVEN widget on 3G connection
- WHEN widget loads
- THEN initial render completes < 2 seconds
- AND transitions complete < 300ms
- AND memory usage stays < 50MB

### AC6: Privacy Protection
- GIVEN customer enters personal data in widget
- WHEN data is submitted
- THEN data is sent via HTTPS
- AND data is not exposed to host page
- AND data is encrypted in transit

### AC7: Analytics Tracking
- GIVEN widget with analytics enabled
- WHEN customers interact with widget
- THEN view events are tracked
- AND step completions are tracked
- AND bookings are tracked
- AND conversion rate is calculated accurately

### AC8: Fallback Behavior
- GIVEN widget fails to load (network error)
- WHEN customer visits page
- THEN fallback message displays
- AND link to standalone booking page is provided
- AND error is logged for support

---

## Technical Approach

### Technology Stack
- **Frontend**: React 18 with TypeScript
- **Build**: Vite for fast bundling
- **Styling**: Tailwind CSS for responsive design
- **State**: React Context for booking flow state
- **API**: Fetch API with async/await
- **Performance**: Code splitting, lazy loading
- **Testing**: React Testing Library, Playwright for E2E

### Widget Architecture

**Component Structure:**
```
BookingWidget
├── WidgetHeader
├── BookingFlow
│   ├── ServiceSelection
│   ├── DateTimeSelection
│   ├── CustomerInfoForm
│   ├── PaymentStep (if required)
│   └── ConfirmationStep
└── WidgetFooter
```

**Key Implementation Points:**

1. **Isolation Techniques**:
   - Shadow DOM for style isolation (inline widgets)
   - iframe for popup and full-page widgets
   - CSS-in-JS with unique class names

2. **State Management**:
   - LocalStorage for progress persistence
   - React Context for flow state
   - Optimistic updates for better UX

3. **Performance Optimization**:
   - Code splitting by step
   - Lazy load images
   - Debounce availability queries
   - Prefetch next step assets

4. **Security**:
   - Public API key (not secret)
   - Rate limiting (100 req/min per IP)
   - CAPTCHA on booking submission
   - CORS restrictions

---

## Testing Strategy

### Unit Tests
- Component rendering with various props
- Booking flow state management
- Form validation logic
- Color customization application
- Responsive layout breakpoints

### Integration Tests
- Widget loads on external website
- Booking API integration
- Analytics event tracking
- Payment processing (if required)
- Error handling and retry logic

### E2E Tests (Playwright)
- Complete booking flow on mobile
- Complete booking flow on desktop
- Widget customization appearance
- Analytics data collection
- Cross-browser compatibility (Chrome, Firefox, Safari)

---

## Success Metrics

- Widget load time < 2s (3G)
- Booking completion rate > 60%
- Mobile conversion rate within 10% of desktop
- Zero style conflicts with host pages
- 85%+ test coverage achieved
- Widget uptime > 99.9%

---

**Next SPEC**: SPEC-CAL-005 (Calendar Integrations)

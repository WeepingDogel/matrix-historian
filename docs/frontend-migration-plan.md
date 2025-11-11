# Frontend Migration Plan: Streamlit to JavaScript Framework

## Executive Summary

This document outlines a comprehensive plan to migrate the Matrix Historian frontend from Streamlit (Python) to a modern JavaScript framework. The migration will improve performance, user experience, and maintainability while preserving all existing functionality.

## Current State Analysis

### Existing Features

#### 1. Message Browsing Page
- **Search**: Full-text message search with query highlighting
- **Filtering**: Filter by room and user
- **Pagination**: Infinite scroll / "Load More" functionality
- **Display**: Message cards with sender, room, content, and relative timestamps
- **User Selection**: Advanced user search and selection with caching
- **Room Selection**: Dropdown with room names and IDs

#### 2. Analytics/Message Analysis Page
- **Activity Overview**: Message trends (line chart) and user activity (pie chart)
- **Word Cloud Analysis**: Word frequency bar chart and word cloud visualization
- **User Interactions**: Network graph and interaction heatmap
- **Topic Analysis**: Topic evolution timeline and topic summary
- **Sentiment Analysis**: Gauge chart with sentiment confidence
- **Activity Heatmap**: Hourly/weekly activity heatmap with statistics
- **Filters**: Time range (days) and room selection

#### 3. Technical Features
- **Caching**: API response caching (300s TTL)
- **Internationalization**: Chinese language support
- **Health Checks**: Health check endpoint support
- **Error Handling**: Graceful error handling with user-friendly messages

### API Endpoints Available

#### Message Endpoints
- `GET /api/v1/messages/` - List messages with filters
- `GET /api/v1/messages/{event_id}` - Get single message
- `GET /api/v1/messages/count` - Get message count
- `GET /api/v1/search/` - Search messages
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/search/` - Search users
- `GET /api/v1/rooms/` - List rooms

#### Analytics Endpoints
- `GET /api/v1/analytics/overview` - Activity overview
- `GET /api/v1/analytics/wordcloud` - Word cloud data
- `GET /api/v1/analytics/user-network` - User interaction network
- `GET /api/v1/analytics/interactions` - User interactions
- `GET /api/v1/analytics/trends` - Message trends
- `GET /api/v1/analytics/sentiment` - Sentiment analysis
- `GET /api/v1/analytics/activity-heatmap` - Activity heatmap
- `GET /api/v1/analytics/topic-evolution` - Topic evolution
- `GET /api/v1/analytics/content-analysis` - Content analysis
- `GET /api/v1/analytics/ai-analysis` - Unified AI analysis
- `GET /api/v1/health` - Health check

## Framework Selection

### Selected Framework: **Vue.js 3 + TypeScript + Vite + DaisyUI**

#### Rationale

1. **Vue.js 3**
   - Progressive framework with excellent developer experience
   - Composition API for better code organization
   - Excellent performance and reactivity system
   - Strong TypeScript support
   - Growing ecosystem with good visualization libraries
   - Easy learning curve and great documentation

2. **TypeScript**
   - Type safety for API responses
   - Better IDE support and autocomplete
   - Reduced runtime errors
   - Improved maintainability

3. **Vite**
   - Fast development server
   - Optimized production builds
   - Excellent HMR (Hot Module Replacement)
   - Modern tooling
   - First-class Vue support

4. **DaisyUI**
   - Beautiful, accessible UI components built on Tailwind CSS
   - Pre-built component classes
   - Theme support out of the box
   - Consistent design system
   - Easy customization

### Technology Stack

#### Core Framework
- **Vue.js 3.4+** - UI framework (Composition API)
- **TypeScript 5+** - Type safety
- **Vite 5+** - Build tool
- **Vue Router 4+** - Client-side routing

#### UI/Styling
- **Tailwind CSS 3+** - Utility-first CSS framework (required by DaisyUI)
- **DaisyUI 4+** - Component library built on Tailwind CSS
- **Lucide Vue** or **Heroicons Vue** - Icon library

#### State Management
- **Pinia 2+** - Official Vue state management
- **VueUse** - Collection of Vue composition utilities
- **@tanstack/vue-query** - Server state management, caching, and synchronization (optional, or use Pinia)

#### Data Visualization
- **Apache ECharts** with **vue-echarts** - Comprehensive charting library
- **Chart.js** with **vue-chartjs** - Alternative chart library
- **wordcloud2.js** - Word cloud visualization
- **vis-network** - Network graph visualization (Vue wrapper available)
- **vue3-heatmap** or custom heatmap component - Heatmap visualization

#### Utilities
- **Axios** - HTTP client
- **date-fns** or **Day.js** - Date manipulation
- **humanize-duration** - Relative time formatting
- **marked** or **markdown-it** - Markdown rendering (if needed)
- **@tanstack/vue-virtual** or **vue-virtual-scroller** - Virtual scrolling for large message lists

#### Internationalization
- **vue-i18n** - Internationalization framework for Vue

#### Development Tools
- **ESLint** - Linting
- **Prettier** - Code formatting
- **Vitest** - Unit testing
- **@vue/test-utils** - Vue component testing utilities

## Project Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   └── fonts/              # Custom fonts if needed
├── src/
│   ├── api/                # API client
│   │   ├── client.ts       # Axios instance
│   │   ├── messages.ts     # Message endpoints
│   │   ├── analytics.ts    # Analytics endpoints
│   │   ├── users.ts        # User endpoints
│   │   └── rooms.ts        # Room endpoints
│   ├── components/         # Vue components
│   │   ├── common/         # Shared components
│   │   │   ├── Button.vue
│   │   │   ├── Input.vue
│   │   │   ├── Select.vue
│   │   │   ├── Loading.vue
│   │   │   ├── ErrorMessage.vue
│   │   │   └── MessageCard.vue
│   │   ├── message-browser/ # Message browsing components
│   │   │   ├── MessageList.vue
│   │   │   ├── MessageSearch.vue
│   │   │   ├── RoomFilter.vue
│   │   │   ├── UserFilter.vue
│   │   │   └── MessageFilters.vue
│   │   └── analytics/      # Analytics components
│   │       ├── ActivityOverview.vue
│   │       ├── WordCloud.vue
│   │       ├── UserNetwork.vue
│   │       ├── TopicAnalysis.vue
│   │       ├── SentimentAnalysis.vue
│   │       └── ActivityHeatmap.vue
│   ├── composables/        # Vue composition functions (like React hooks)
│   │   ├── useMessages.ts
│   │   ├── useAnalytics.ts
│   │   ├── useInfiniteScroll.ts
│   │   └── useDebounce.ts
│   ├── layouts/            # Layout components
│   │   ├── MainLayout.vue
│   │   └── Sidebar.vue
│   ├── views/              # Page components (Vue Router views)
│   │   ├── MessageBrowser.vue
│   │   ├── Analytics.vue
│   │   └── NotFound.vue
│   ├── stores/             # Pinia stores
│   │   ├── messageStore.ts
│   │   ├── userStore.ts
│   │   └── analyticsStore.ts
│   ├── types/              # TypeScript types
│   │   ├── message.ts
│   │   ├── analytics.ts
│   │   ├── user.ts
│   │   └── room.ts
│   ├── utils/              # Utility functions
│   │   ├── date.ts         # Date formatting
│   │   ├── highlight.ts    # Text highlighting
│   │   └── constants.ts    # Constants
│   ├── i18n/               # Internationalization
│   │   ├── locales/
│   │   │   ├── en.json
│   │   │   └── zh.json
│   │   └── index.ts
│   ├── router/             # Vue Router configuration
│   │   └── index.ts
│   ├── App.vue             # Root component
│   ├── main.ts             # Entry point
│   └── vite-env.d.ts       # Vite type definitions
├── .env.example
├── .env.local
├── .eslintrc.json
├── .prettierrc
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

## Component Architecture

### 1. Message Browser Page

#### Components
```
MessageBrowser (View)
├── Sidebar
│   ├── MessageSearch
│   ├── RoomFilter
│   └── UserFilter
└── MainContent
    ├── MessageList
    │   ├── MessageCard (multiple)
    │   └── LoadMoreButton
    └── StatsDisplay
```

#### State Management
- **Server State**: Pinia stores with API calls, or @tanstack/vue-query
- **Client State**: Vue reactive refs for filters, pagination
- **Caching**: Pinia stores with caching logic, or vue-query caching (5min default)

#### Features
- **Search**: Debounced search input (300ms delay) using VueUse
- **Filters**: Room and user selection with search
- **Pagination**: Infinite scroll or "Load More" button
- **Virtual Scrolling**: For large message lists (vue-virtual-scroller)
- **Highlighting**: Highlight search terms in message content
- **Relative Time**: Display "2 hours ago" format

### 2. Analytics Page

#### Components
```
Analytics (View)
├── Sidebar
│   ├── TimeRangeSlider
│   └── RoomFilter
└── MainContent
    ├── ActivityOverview
    │   ├── MessageTrendsChart
    │   └── UserActivityChart
    ├── WordCloudAnalysis
    │   ├── WordFrequencyChart
    │   └── WordCloudVisualization
    ├── UserInteractions
    │   ├── UserNetworkGraph
    │   └── InteractionHeatmap
    ├── TopicAnalysis
    │   ├── TopicEvolutionChart
    │   └── TopicSummary
    ├── SentimentAnalysis
    │   └── SentimentGauge
    └── ActivityHeatmap
        ├── HeatmapChart
        └── ActivityStats
```

#### State Management
- **Server State**: Pinia stores for all analytics data, or @tanstack/vue-query
- **Client State**: Vue reactive refs for filters (days, room_id)
- **Caching**: Pinia stores with caching logic, or vue-query with staleTime based on data freshness needs

#### Features
- **Charts**: Interactive charts with zoom, pan, tooltips (ECharts)
- **Loading States**: Skeleton loaders while data loads (DaisyUI skeleton component)
- **Error Handling**: Graceful error messages (DaisyUI alert component)
- **Filtering**: Time range and room filtering
- **Real-time Updates**: Optional polling for fresh data

## API Integration

### API Client Setup

```typescript
// src/api/client.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use((config) => {
  console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('[API Error]', error);
    return Promise.reject(error);
  }
);
```

### Pinia Store for Messages

```typescript
// src/stores/messageStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { getMessages, searchMessages, type MessageFilters, type MessageResponse } from '../api/messages';

export const useMessageStore = defineStore('messages', () => {
  const messages = ref<Message[]>([]);
  const total = ref(0);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const filters = ref<MessageFilters>({});
  const hasMore = ref(true);
  const nextSkip = ref(0);

  const fetchMessages = async (newFilters?: MessageFilters) => {
    if (newFilters) {
      filters.value = newFilters;
      messages.value = [];
      nextSkip.value = 0;
    }

    loading.value = true;
    error.value = null;

    try {
      const params = { ...filters.value, skip: nextSkip.value };
      const response: MessageResponse = filters.value.query
        ? await searchMessages(params)
        : await getMessages(params);

      messages.value.push(...response.messages);
      total.value = response.total;
      hasMore.value = response.has_more;
      nextSkip.value = response.next_skip || 0;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch messages';
    } finally {
      loading.value = false;
    }
  };

  const loadMore = async () => {
    if (hasMore.value && !loading.value) {
      await fetchMessages();
    }
  };

  return {
    messages,
    total,
    loading,
    error,
    filters,
    hasMore,
    fetchMessages,
    loadMore,
  };
});
```

### Vue Composable for Messages

```typescript
// src/composables/useMessages.ts
import { computed, watch } from 'vue';
import { useMessageStore } from '../stores/messageStore';
import { useDebounceFn } from '@vueuse/core';

export function useMessages() {
  const store = useMessageStore();

  const debouncedFetch = useDebounceFn(() => {
    store.fetchMessages();
  }, 300);

  watch(
    () => store.filters,
    () => {
      debouncedFetch();
    },
    { deep: true }
  );

  return {
    messages: computed(() => store.messages),
    total: computed(() => store.total),
    loading: computed(() => store.loading),
    error: computed(() => store.error),
    hasMore: computed(() => store.hasMore),
    loadMore: store.loadMore,
    updateFilters: (filters: MessageFilters) => {
      store.filters = { ...store.filters, ...filters };
    },
  };
}
```

### Type Definitions

```typescript
// src/types/message.ts
export interface Message {
  event_id: string;
  room_id: string;
  sender_id: string;
  content: string;
  timestamp: string;
  room: Room;
  sender: User;
}

export interface MessageResponse {
  messages: Message[];
  total: number;
  has_more: boolean;
  next_skip: number | null;
}

export interface MessageFilters {
  query?: string;
  room_id?: string;
  user_id?: string;
  skip?: number;
  limit?: number;
}
```

## State Management Strategy

### Server State (Pinia Stores)
- All API data (messages, analytics, users, rooms)
- Manual caching logic or use @tanstack/vue-query for automatic caching
- Refetching and synchronization
- Optimistic updates where appropriate

### Client State (Vue Reactive Refs)
- UI state (sidebar open/closed, modal states)
- Form inputs (search query, filters)
- Pagination state (handled by Pinia stores)

### Global State (Pinia Stores)
- User preferences (theme, language)
- UI settings (items per page, default filters)
- App-wide configuration

## UI/UX Improvements

### Design System
- **Color Scheme**: Modern, accessible color palette
- **Typography**: Clear hierarchy with readable fonts
- **Spacing**: Consistent spacing system
- **Components**: Reusable, accessible components

### User Experience
1. **Loading States**: Skeleton loaders instead of spinners
2. **Error States**: Helpful error messages with retry options
3. **Empty States**: Informative empty state messages
4. **Responsive Design**: Mobile-friendly layout
5. **Accessibility**: ARIA labels, keyboard navigation
6. **Performance**: Code splitting, lazy loading, virtual scrolling

### Visualizations
1. **Interactive Charts**: Zoom, pan, tooltips, legends
2. **Responsive Charts**: Adapt to container size
3. **Loading Animations**: Smooth transitions
4. **Export Options**: Download charts as images/PDF

## Internationalization

### Setup
```typescript
// src/i18n/index.ts
import { createI18n } from 'vue-i18n';
import en from './locales/en.json';
import zh from './locales/zh.json';

export default createI18n({
  legacy: false,
  locale: 'zh', // Default language
  fallbackLocale: 'en',
  messages: {
    en,
    zh,
  },
});
```

### Usage in Components
```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>

<template>
  <h1>{{ t('messageBrowser.title') }}</h1>
</template>
```

## Deployment Strategy

### Build Process
1. **Development**: `npm run dev` - Vite dev server
2. **Build**: `npm run build` - Production build
3. **Preview**: `npm run preview` - Preview production build

### Docker Configuration

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Note: The Dockerfile is the same for Vue.js as it builds to static files.

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Compose Update

```yaml
# src/docker-compose.yml
services:
  app:
    # ... existing config ...

  webui:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - app
    environment:
      - VITE_API_URL=http://localhost:8001/api/v1
    restart: always
```

## Migration Path

### Phase 1: Setup and Infrastructure (Week 1)
- [ ] Initialize Vue 3 + TypeScript + Vite project
- [ ] Set up Tailwind CSS and DaisyUI
- [ ] Configure ESLint, Prettier, and testing
- [ ] Set up API client and Pinia stores
- [ ] Set up Vue Router
- [ ] Create basic layout with DaisyUI components
- [ ] Configure vue-i18n

### Phase 2: Message Browser (Week 2)
- [ ] Implement message list component with DaisyUI cards
- [ ] Implement search functionality with debouncing
- [ ] Implement room and user filters with DaisyUI select
- [ ] Implement pagination/infinite scroll
- [ ] Implement message card with highlighting
- [ ] Add loading states with DaisyUI skeleton
- [ ] Add error states with DaisyUI alert

### Phase 3: Analytics Page (Week 3)
- [ ] Implement activity overview charts (ECharts)
- [ ] Implement word cloud visualization
- [ ] Implement user network graph (vis-network)
- [ ] Implement topic analysis charts
- [ ] Implement sentiment analysis gauge
- [ ] Implement activity heatmap
- [ ] Add filters and time range selector with DaisyUI components

### Phase 4: Polish and Optimization (Week 4)
- [ ] Complete internationalization (vue-i18n)
- [ ] Optimize performance (code splitting, lazy loading)
- [ ] Add virtual scrolling for large lists
- [ ] Improve responsive design with DaisyUI responsive classes
- [ ] Add accessibility features
- [ ] Write tests with Vitest and @vue/test-utils

### Phase 5: Deployment and Migration (Week 5)
- [ ] Create Docker configuration
- [ ] Update docker-compose.yml
- [ ] Test deployment
- [ ] Update documentation
- [ ] Deploy to production
- [ ] Monitor and fix issues

## Testing Strategy

### Unit Tests
- Component rendering tests (@vue/test-utils)
- Composable tests
- Utility function tests
- API client tests
- Pinia store tests

### Integration Tests
- Page navigation tests (Vue Router)
- Filter interaction tests
- API integration tests

### E2E Tests (Optional)
- Playwright or Cypress tests
- Critical user flows
- Cross-browser testing

## Performance Optimization

### Code Splitting
- Route-based code splitting
- Component lazy loading
- Dynamic imports for heavy libraries

### Caching
- React Query caching (5min default)
- Browser caching for static assets
- Service Worker for offline support (optional)

### Bundle Optimization
- Tree shaking
- Minification
- Compression (gzip/brotli)
- Image optimization

### Runtime Optimization
- Virtual scrolling for long lists
- Debounced search inputs
- Memoized components
- Optimized re-renders

## Security Considerations

### API Security
- CORS configuration
- API key management (if needed)
- Rate limiting handling
- Error message sanitization

### Frontend Security
- XSS prevention
- CSRF protection
- Content Security Policy
- Secure headers

## Monitoring and Analytics

### Error Tracking
- Sentry or similar error tracking
- Vue error handlers (app.config.errorHandler)
- API error logging

### Performance Monitoring
- Web Vitals tracking
- API response time monitoring
- Bundle size monitoring

### User Analytics (Optional)
- Google Analytics or privacy-friendly alternative
- User interaction tracking
- Feature usage statistics

## Documentation

### Developer Documentation
- Setup instructions
- Component documentation (Vue component docs)
- API integration guide
- Pinia store usage guide
- Contributing guidelines

### User Documentation
- User guide
- Feature documentation
- FAQ

## Success Metrics

### Performance Metrics
- Initial page load < 2s
- Time to interactive < 3s
- API response time < 500ms
- Bundle size < 500KB (gzipped)

### User Experience Metrics
- Page load success rate > 99%
- Error rate < 1%
- User satisfaction score
- Feature adoption rate

## Risks and Mitigation

### Risks
1. **API Compatibility**: API changes breaking frontend
   - **Mitigation**: Type-safe API client, versioned APIs
2. **Performance Issues**: Large datasets causing slow rendering
   - **Mitigation**: Virtual scrolling, pagination, caching, Vue's reactivity optimization
3. **Browser Compatibility**: Older browsers not supported
   - **Mitigation**: Modern browser support (Vue 3 requires modern browsers), polyfills if needed
4. **Migration Complexity**: Difficult to migrate all features
   - **Mitigation**: Phased migration, feature parity checklist
5. **DaisyUI Learning Curve**: Team unfamiliar with DaisyUI
   - **Mitigation**: Good documentation, component examples, DaisyUI theme customization

## Timeline Summary

- **Week 1**: Setup and infrastructure
- **Week 2**: Message browser implementation
- **Week 3**: Analytics page implementation
- **Week 4**: Polish and optimization
- **Week 5**: Deployment and migration

**Total Estimated Time**: 5 weeks (1 developer)

## Next Steps

1. Review and approve this plan
2. Read the [Q&A document](./frontend-migration-qa.md) for common questions
3. Set up development environment
4. Create project repository
5. Begin Phase 1 implementation
6. Regular progress reviews and adjustments

## References

- [Vue.js Documentation](https://vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vue Router Documentation](https://router.vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [DaisyUI Documentation](https://daisyui.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Apache ECharts Documentation](https://echarts.apache.org/)
- [VueUse Documentation](https://vueuse.org/)
- [vue-i18n Documentation](https://vue-i18n.intlify.dev/)

## Appendix: Package.json Dependencies

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.0",
    "date-fns": "^2.30.0",
    "dayjs": "^1.11.10",
    "humanize-duration": "^3.31.0",
    "vue-i18n": "^9.8.0",
    "echarts": "^5.4.3",
    "vue-echarts": "^6.6.9",
    "wordcloud2": "^1.2.2",
    "vis-network": "^9.1.9",
    "@vueuse/core": "^10.7.0",
    "@vueuse/components": "^10.7.0",
    "lucide-vue-next": "^0.294.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@vitejs/plugin-vue": "^5.0.0",
    "@vue/test-utils": "^2.4.3",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vue-tsc": "^1.8.25",
    "tailwindcss": "^3.3.6",
    "daisyui": "^4.4.19",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "eslint": "^8.54.0",
    "@typescript-eslint/parser": "^6.13.0",
    "@typescript-eslint/eslint-plugin": "^6.13.0",
    "eslint-plugin-vue": "^9.18.1",
    "prettier": "^3.1.0",
    "prettier-plugin-tailwindcss": "^0.5.9",
    "vitest": "^1.0.4",
    "@vitest/ui": "^1.0.4"
  }
}
```

## Appendix: Tailwind and DaisyUI Configuration

```javascript
// tailwind.config.js
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: ['light', 'dark', 'cupcake'], // Add more themes as needed
    darkTheme: 'dark',
    base: true,
    styled: true,
    utils: true,
    prefix: '',
    logs: true,
    themeRoot: ':root',
  },
};
```

## Appendix: Example Vue Component

```vue
<!-- src/components/MessageCard.vue -->
<script setup lang="ts">
import { computed } from 'vue';
import type { Message } from '@/types/message';
import { formatRelativeTime } from '@/utils/date';
import { highlightText } from '@/utils/highlight';

interface Props {
  message: Message;
  searchQuery?: string;
}

const props = defineProps<Props>();

const highlightedContent = computed(() => 
  props.searchQuery 
    ? highlightText(props.message.content, props.searchQuery)
    : props.message.content
);

const relativeTime = computed(() => 
  formatRelativeTime(props.message.timestamp)
);
</script>

<template>
  <div class="card bg-base-100 shadow-md mb-4">
    <div class="card-body">
      <div class="flex justify-between items-start">
        <div class="flex-1">
          <h3 class="card-title text-sm">
            {{ message.sender.display_name || message.sender.user_id }}
            <span class="text-xs text-base-content/60">
              in {{ message.room.name || message.room.room_id }}
            </span>
          </h3>
          <p 
            class="mt-2" 
            v-html="highlightedContent"
          ></p>
        </div>
        <div class="text-xs text-base-content/60 ml-4">
          {{ relativeTime }}
        </div>
      </div>
    </div>
  </div>
</template>
```


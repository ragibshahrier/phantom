# Frontend Event Deletion Sync Fix

## Problem
When events were deleted via chat, the changes were not immediately reflected in the frontend. Users had to manually reload the page to see the deleted events removed from the timeline.

## Root Cause
The frontend's `summonSpirit` function in `SeanceRoom.tsx` only refreshed the events list when `createdEvents.length > 0`, but it didn't check for deleted events. The backend was returning `events_deleted` in the response, but the frontend wasn't handling it.

## Solution

### 1. Updated Types (`phantom_frontend/types/index.ts`)

**Added `events_deleted` to ChatResponse:**
```typescript
export interface ChatResponse {
  response: string;
  events_created?: Event[];
  events_modified?: Event[];
  events_deleted?: Array<{id: number; title: string; start_time: string}>;  // NEW
  intent_detected?: string;
}
```

**Updated UseChatReturn interface:**
```typescript
export interface UseChatReturn {
  chatHistory: ChatHistoryItem[];
  isLoading: boolean;
  error: string | null;
  sendMessage(message: string): Promise<{created: Event[], deleted: number[]}>;  // CHANGED
  clearHistory(): void;
}
```

### 2. Updated useChat Hook (`phantom_frontend/hooks/useChat.ts`)

**Changed return type from `Promise<Event[]>` to `Promise<{created: Event[], deleted: number[]}>`:**

```typescript
const sendMessage = useCallback(async (message: string): Promise<{created: Event[], deleted: number[]}> => {
  // ... existing code ...
  
  // Return created and deleted events
  return {
    created: response.events_created || [],
    deleted: (response.events_deleted || []).map(e => e.id)
  };
}, []);
```

### 3. Updated SeanceRoom (`phantom_frontend/pages/SeanceRoom.tsx`)

**Updated `summonSpirit` to handle both created and deleted events:**

```typescript
const summonSpirit = async (message: string) => {
  // Send message to Phantom and get created/deleted events
  const {created, deleted} = await sendMessage(message);
  
  // If events were created or deleted, refresh the timeline
  if (created.length > 0 || deleted.length > 0) {
    await refreshEvents();
  }
};
```

## How It Works Now

1. User sends a deletion command via chat (e.g., "delete my dinner")
2. Backend processes the request and returns:
   ```json
   {
     "response": "I have deleted 1 event for you.",
     "events_deleted": [{"id": 123, "title": "dinner", "start_time": "..."}],
     "intent": "delete"
   }
   ```
3. Frontend `useChat` hook extracts the deleted event IDs
4. `summonSpirit` checks if any events were created OR deleted
5. If yes, calls `refreshEvents()` to fetch the updated event list
6. Timeline updates immediately without requiring a page reload

## Benefits

- ✅ Immediate UI updates when events are deleted
- ✅ Consistent behavior with event creation
- ✅ No manual page reload required
- ✅ Better user experience
- ✅ Type-safe implementation

## Files Modified

1. `phantom_frontend/types/index.ts` - Added events_deleted to ChatResponse, updated UseChatReturn
2. `phantom_frontend/hooks/useChat.ts` - Changed return type to include deleted events
3. `phantom_frontend/pages/SeanceRoom.tsx` - Updated summonSpirit to refresh on deletions

## Testing

To test the fix:
1. Create some events via chat
2. Delete an event via chat (e.g., "delete my dinner")
3. Verify the event disappears from the timeline immediately
4. No page reload should be required

The fix ensures that any chat operation that modifies events (create or delete) will automatically refresh the timeline.

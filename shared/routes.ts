import { z } from 'zod';
import { 
  insertBookingSchema, 
  insertMessageSchema,
  services,
  stylists,
  testimonials,
  offers
} from './schema';

export const errorSchemas = {
  validation: z.object({
    message: z.string(),
    field: z.string().optional(),
  }),
  notFound: z.object({
    message: z.string(),
  }),
  internal: z.object({
    message: z.string(),
  }),
};

export const api = {
  services: {
    list: {
      method: 'GET' as const,
      path: '/api/services',
      responses: {
        200: z.array(z.custom<typeof services.$inferSelect>()),
      },
    },
    get: {
      method: 'GET' as const,
      path: '/api/services/:id',
      responses: {
        200: z.custom<typeof services.$inferSelect>(),
        404: errorSchemas.notFound,
      },
    },
  },
  stylists: {
    list: {
      method: 'GET' as const,
      path: '/api/stylists',
      responses: {
        200: z.array(z.custom<typeof stylists.$inferSelect>()),
      },
    },
    get: {
      method: 'GET' as const,
      path: '/api/stylists/:id',
      responses: {
        200: z.custom<typeof stylists.$inferSelect>(),
        404: errorSchemas.notFound,
      },
    },
  },
  testimonials: {
    list: {
      method: 'GET' as const,
      path: '/api/testimonials',
      responses: {
        200: z.array(z.custom<typeof testimonials.$inferSelect>()),
      },
    },
  },
  offers: {
    list: {
      method: 'GET' as const,
      path: '/api/offers',
      responses: {
        200: z.array(z.custom<typeof offers.$inferSelect>()),
      },
    },
  },
  bookings: {
    create: {
      method: 'POST' as const,
      path: '/api/bookings',
      input: insertBookingSchema,
      responses: {
        201: z.custom<typeof bookings.$inferSelect>(),
        400: errorSchemas.validation,
      },
    },
  },
  messages: {
    create: {
      method: 'POST' as const,
      path: '/api/messages',
      input: insertMessageSchema,
      responses: {
        201: z.custom<typeof messages.$inferSelect>(),
        400: errorSchemas.validation,
      },
    },
  },
};

export function buildUrl(path: string, params?: Record<string, string | number>): string {
  let url = path;
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (url.includes(`:${key}`)) {
        url = url.replace(`:${key}`, String(value));
      }
    });
  }
  return url;
}

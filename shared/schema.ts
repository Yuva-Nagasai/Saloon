import { pgTable, text, serial, integer, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// === TABLE DEFINITIONS ===

export const services = pgTable("services", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  category: text("category").notNull(), // e.g., "Hair", "Skin", "Nails", "Spa"
  price: integer("price").notNull(), // stored in cents
  duration: integer("duration").notNull(), // in minutes
  image: text("image").notNull(),
  isFeatured: boolean("is_featured").default(false),
});

export const stylists = pgTable("stylists", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  role: text("role").notNull(), // e.g., "Senior Stylist", "Colorist"
  bio: text("bio").notNull(),
  image: text("image").notNull(),
  specialties: text("specialties").array(),
});

export const testimonials = pgTable("testimonials", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  role: text("role"), // e.g., "Regular Client"
  content: text("content").notNull(),
  rating: integer("rating").notNull(), // 1-5
  avatar: text("avatar"),
});

export const offers = pgTable("offers", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  code: text("code"),
  discount: text("discount").notNull(), // e.g. "20% OFF"
  expiry: text("expiry"),
});

export const bookings = pgTable("bookings", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull(),
  phone: text("phone").notNull(),
  serviceId: integer("service_id").notNull(),
  stylistId: integer("stylist_id"),
  date: text("date").notNull(), // Simplified for UI demo
  time: text("time").notNull(),
  message: text("message"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const messages = pgTable("messages", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull(),
  subject: text("subject").notNull(),
  message: text("message").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

// === SCHEMAS ===

export const insertServiceSchema = createInsertSchema(services).omit({ id: true });
export const insertStylistSchema = createInsertSchema(stylists).omit({ id: true });
export const insertTestimonialSchema = createInsertSchema(testimonials).omit({ id: true });
export const insertOfferSchema = createInsertSchema(offers).omit({ id: true });
export const insertBookingSchema = createInsertSchema(bookings).omit({ id: true, createdAt: true });
export const insertMessageSchema = createInsertSchema(messages).omit({ id: true, createdAt: true });

// === EXPLICIT API TYPES ===

export type Service = typeof services.$inferSelect;
export type Stylist = typeof stylists.$inferSelect;
export type Testimonial = typeof testimonials.$inferSelect;
export type Offer = typeof offers.$inferSelect;
export type Booking = typeof bookings.$inferSelect;
export type Message = typeof messages.$inferSelect;

export type InsertBooking = z.infer<typeof insertBookingSchema>;
export type InsertMessage = z.infer<typeof insertMessageSchema>;

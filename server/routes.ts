import type { Express } from "express";
import type { Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // Services
  app.get(api.services.list.path, async (req, res) => {
    const services = await storage.getServices();
    res.json(services);
  });

  app.get(api.services.get.path, async (req, res) => {
    const service = await storage.getService(Number(req.params.id));
    if (!service) {
      return res.status(404).json({ message: "Service not found" });
    }
    res.json(service);
  });

  // Stylists
  app.get(api.stylists.list.path, async (req, res) => {
    const stylists = await storage.getStylists();
    res.json(stylists);
  });
  
  app.get(api.stylists.get.path, async (req, res) => {
    const stylist = await storage.getStylist(Number(req.params.id));
    if (!stylist) {
      return res.status(404).json({ message: "Stylist not found" });
    }
    res.json(stylist);
  });

  // Testimonials
  app.get(api.testimonials.list.path, async (req, res) => {
    const testimonials = await storage.getTestimonials();
    res.json(testimonials);
  });
  
  // Offers
  app.get(api.offers.list.path, async (req, res) => {
    const offers = await storage.getOffers();
    res.json(offers);
  });

  // Bookings
  app.post(api.bookings.create.path, async (req, res) => {
    try {
      const input = api.bookings.create.input.parse(req.body);
      const booking = await storage.createBooking(input);
      res.status(201).json(booking);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({
          message: err.errors[0].message,
          field: err.errors[0].path.join('.'),
        });
      }
      throw err;
    }
  });

  // Messages
  app.post(api.messages.create.path, async (req, res) => {
    try {
      const input = api.messages.create.input.parse(req.body);
      const message = await storage.createMessage(input);
      res.status(201).json(message);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({
          message: err.errors[0].message,
          field: err.errors[0].path.join('.'),
        });
      }
      throw err;
    }
  });

  return httpServer;
}

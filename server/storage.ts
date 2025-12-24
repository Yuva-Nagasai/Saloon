import { 
  services, stylists, testimonials, offers, bookings, messages,
  type Service, type Stylist, type Testimonial, type Offer, type Booking, type Message,
  type InsertBooking, type InsertMessage
} from "@shared/schema";

export interface IStorage {
  // Services
  getServices(): Promise<Service[]>;
  getService(id: number): Promise<Service | undefined>;
  
  // Stylists
  getStylists(): Promise<Stylist[]>;
  getStylist(id: number): Promise<Stylist | undefined>;
  
  // Testimonials
  getTestimonials(): Promise<Testimonial[]>;
  
  // Offers
  getOffers(): Promise<Offer[]>;
  
  // Bookings
  createBooking(booking: InsertBooking): Promise<Booking>;
  
  // Messages
  createMessage(message: InsertMessage): Promise<Message>;
}

export class MemStorage implements IStorage {
  private services: Map<number, Service>;
  private stylists: Map<number, Stylist>;
  private testimonials: Map<number, Testimonial>;
  private offers: Map<number, Offer>;
  private bookings: Map<number, Booking>;
  private messages: Map<number, Message>;
  
  private currentId: { [key: string]: number };

  constructor() {
    this.services = new Map();
    this.stylists = new Map();
    this.testimonials = new Map();
    this.offers = new Map();
    this.bookings = new Map();
    this.messages = new Map();
    
    this.currentId = {
      services: 1,
      stylists: 1,
      testimonials: 1,
      offers: 1,
      bookings: 1,
      messages: 1,
    };
    
    this.seedData();
  }

  private seedData() {
    // Seed Services
    const seedServices: Omit<Service, "id">[] = [
      {
        title: "Signature Haircut & Style",
        description: "A precision cut tailored to your face shape and lifestyle, finished with a luxury blowout.",
        category: "Hair",
        price: 8500, // $85.00
        duration: 60,
        image: "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&q=80",
        isFeatured: true
      },
      {
        title: "Balayage & Color Correction",
        description: "Hand-painted highlights for a natural, sun-kissed look or complete color transformation.",
        category: "Hair",
        price: 25000, // $250.00
        duration: 180,
        image: "https://images.unsplash.com/photo-1560869713-7d0a29430803?auto=format&fit=crop&q=80",
        isFeatured: true
      },
      {
        title: "Luxury Spa Manicure",
        description: "Exfoliation, mask, massage, and polish application for rejuvenated hands.",
        category: "Nails",
        price: 4500, // $45.00
        duration: 45,
        image: "https://images.unsplash.com/photo-1632345031435-8727f6897d53?auto=format&fit=crop&q=80",
        isFeatured: false
      },
      {
        title: "Deep Tissue Massage",
        description: "Therapeutic massage focusing on realignment of deeper layers of muscles and connective tissue.",
        category: "Spa",
        price: 12000, // $120.00
        duration: 60,
        image: "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?auto=format&fit=crop&q=80",
        isFeatured: true
      },
      {
        title: "Rejuvenating Facial",
        description: "Customized facial treatment to cleanse, exfoliate, and hydrate your skin.",
        category: "Skin",
        price: 9500, // $95.00
        duration: 75,
        image: "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&q=80",
        isFeatured: false
      },
      {
        title: "Keratin Treatment",
        description: "Smoothing treatment to eliminate frizz and add shine for up to 4 months.",
        category: "Hair",
        price: 30000, // $300.00
        duration: 150,
        image: "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?auto=format&fit=crop&q=80",
        isFeatured: false
      }
    ];

    seedServices.forEach(s => {
      const id = this.currentId.services++;
      this.services.set(id, { ...s, id });
    });

    // Seed Stylists
    const seedStylists: Omit<Stylist, "id">[] = [
      {
        name: "Elena Rossi",
        role: "Creative Director",
        bio: "With over 15 years of experience in Milan and Paris, Elena brings international flair to every cut.",
        image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80",
        specialties: ["Precision Cutting", "Avant-Garde Styling"]
      },
      {
        name: "David Chen",
        role: "Master Colorist",
        bio: "David specializes in creating multidimensional color that enhances natural beauty.",
        image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80",
        specialties: ["Balayage", "Color Correction", "Blondes"]
      },
      {
        name: "Sarah Jenkins",
        role: "Senior Stylist",
        bio: "Sarah is known for her ability to work with all textures and create effortless, wearable styles.",
        image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&q=80",
        specialties: ["Curly Hair", "Bridal Styling"]
      }
    ];

    seedStylists.forEach(s => {
      const id = this.currentId.stylists++;
      this.stylists.set(id, { ...s, id });
    });

    // Seed Testimonials
    const seedTestimonials: Omit<Testimonial, "id">[] = [
      {
        name: "Jessica M.",
        role: "Loyal Client",
        content: "The best salon experience I've ever had. Elena understood exactly what I wanted and delivered beyond expectations.",
        rating: 5,
        avatar: "https://randomuser.me/api/portraits/women/44.jpg"
      },
      {
        name: "Michael T.",
        role: "New Client",
        content: "Incredible atmosphere and professional service. The hot towel shave was perfection.",
        rating: 5,
        avatar: "https://randomuser.me/api/portraits/men/32.jpg"
      },
      {
        name: "Sophia L.",
        role: "VIP Member",
        content: "I've been coming here for years. The consistency and quality are unmatched in the city.",
        rating: 5,
        avatar: "https://randomuser.me/api/portraits/women/68.jpg"
      }
    ];

    seedTestimonials.forEach(t => {
      const id = this.currentId.testimonials++;
      this.testimonials.set(id, { ...t, id });
    });
    
    // Seed Offers
    const seedOffers: Omit<Offer, "id">[] = [
      {
        title: "New Client Special",
        description: "Enjoy a complimentary treatment with your first haircut.",
        code: "WELCOME20",
        discount: "Complimentary Treatment",
        expiry: "Ongoing"
      },
      {
        title: "Summer Glow Package",
        description: "Full balayage, gloss, and style for a refreshed look.",
        code: "SUMMERGLOW",
        discount: "15% OFF",
        expiry: "August 31, 2025"
      }
    ];
    
    seedOffers.forEach(o => {
      const id = this.currentId.offers++;
      this.offers.set(id, { ...o, id });
    });
  }

  // Implementation of interface methods
  async getServices(): Promise<Service[]> {
    return Array.from(this.services.values());
  }

  async getService(id: number): Promise<Service | undefined> {
    return this.services.get(id);
  }

  async getStylists(): Promise<Stylist[]> {
    return Array.from(this.stylists.values());
  }
  
  async getStylist(id: number): Promise<Stylist | undefined> {
    return this.stylists.get(id);
  }

  async getTestimonials(): Promise<Testimonial[]> {
    return Array.from(this.testimonials.values());
  }
  
  async getOffers(): Promise<Offer[]> {
    return Array.from(this.offers.values());
  }

  async createBooking(insertBooking: InsertBooking): Promise<Booking> {
    const id = this.currentId.bookings++;
    const booking: Booking = { 
      ...insertBooking, 
      id,
      stylistId: insertBooking.stylistId ?? null,
      message: insertBooking.message ?? null,
      createdAt: new Date()
    };
    this.bookings.set(id, booking);
    return booking;
  }
  
  async createMessage(insertMessage: InsertMessage): Promise<Message> {
    const id = this.currentId.messages++;
    const message: Message = {
      ...insertMessage,
      id,
      createdAt: new Date()
    };
    this.messages.set(id, message);
    return message;
  }
}

export const storage = new MemStorage();

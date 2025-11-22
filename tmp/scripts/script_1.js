
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        // Brgy Tamago Official Brand Colors
                        'brand-gold': '#fdbd16',        // Primary Gold/Yellow
                        'brand-red': '#f22524',         // Primary Red
                        'brand-black': '#1f1f20',       // Dark Background
                        'brand-white': '#ffffff',       // White
                        'brand-beige': '#e3c293',       // Tan/Beige accent
                        'brand-orange': '#ef6d1f',      // Orange accent
                        'brand-gray': '#585858',        // Gray
                        
                        // Derived shades for UI
                        'brand-gold-light': '#ffd03a',  // Lighter gold
                        'brand-gold-dark': '#e5aa00',   // Darker gold
                        'brand-gray-light': '#6E6E6E',  // Lighter gray
                        'brand-gray-dark': '#3A3A3A',   // Darker gray
                        'brand-red-light': '#ff4447',   // Lighter red
                        'brand-red-dark': '#d01619',    // Darker red
                        
                        // Legacy gaming colors (mapped to new colors)
                        'gaming-dark': '#1f1f20',       // Now uses brand-black
                        'neon-blue': '#fdbd16',         // Now uses brand-gold
                        'neon-purple': '#f22524',       // Now uses brand-red
                        'neon-pink': '#FF4447',         // Light red variant
                        'neon-green': '#FEBD11',        // Gold for success
                        'neon-yellow': '#FFCF3A',       // Light gold
                    },
                    fontFamily: {
                        'gaming': ['Orbitron', 'sans-serif'],
                        'body': ['Rajdhani', 'sans-serif'],
                    },
                }
            }
        }
    
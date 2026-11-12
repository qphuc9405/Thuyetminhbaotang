/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#F2ECE0', paper2: '#E8DFCF', card: '#FAF6EE', ink: '#1C1915', ink2: '#3A332B',
        earth: '#6B5440', earth2: '#9C8468', flag: '#A6261C', river: '#22414F', river2: '#3E6475', rule: '#CFC3AE',
        // giữ tên cũ để tương thích
        sepia: '#6B5440', oxblood: '#A6261C', olive: '#4d5a3a',
      },
      fontFamily: {
        serif: ['"Noto Serif"', 'Georgia', '"Noto Serif SC"', '"Songti SC"', 'serif'],
        sans: ['"Be Vietnam Pro"', 'system-ui', '-apple-system', '"Segoe UI"', '"PingFang SC"', '"Microsoft YaHei"', 'sans-serif'],
      },
      maxWidth: { prose2: '42rem' },
      keyframes: {
        kenburns: { '0%': { transform: 'scale(1.06)' }, '100%': { transform: 'scale(1.0)' } },
        rise: { '0%': { opacity: '0', transform: 'translateY(18px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
      },
      animation: { kenburns: 'kenburns 14s ease-out both', rise: 'rise .9s cubic-bezier(.2,.7,.2,1) both' },
    },
  },
  plugins: [],
}

/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./popup.html",
        "./src/**/*.{js,ts,jsx,tsx}",
        "./popup/**/*.{js,ts,jsx,tsx}",
        "./content/**/*.{js,ts,jsx,tsx}"
    ],
    theme: {
        extend: {
            colors: {
                background: "#0f172a", // Slate 900
                surface: "rgba(30, 41, 59, 0.7)", // Slate 800 with opacity
                primary: "#38bdf8", // Sky 400
                secondary: "#818cf8", // Indigo 400
                accent: "#f472b6", // Pink 400
                success: "#22c55e", // Green 500
                danger: "#ef4444", // Red 500
                warning: "#eab308", // Yellow 500
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'spin-slow': 'spin 3s linear infinite',
            }
        },
    },
    plugins: [],
}

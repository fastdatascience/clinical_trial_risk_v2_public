/** @type {import('tailwindcss').Config} */
import withMT from "@material-tailwind/react/utils/withMT";
export default withMT({
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        dmsans: ["DM Sans", "sans-serif"],
        poppins: ["Poppins", "sans-serif"],
      },
      colors: {
        green_primary: "#57ca96",
        green_secondary: "#ebf9f3",
        active_accent: "#f7f7f7",
        Extra_Light_Gray: "#C6CFD2",
        light_gray_bg: "#f1f5f9",
        text_primary: "#21577A",
        text_secondary: "#64748B",
        Gray: "#F8F8F8",
        Green: "#60CC9B",
        Light_Green: "#C7EADA",
      },
      borderRadius: {
        large: "57px",
      },
    },
  },
  plugins: [],
});

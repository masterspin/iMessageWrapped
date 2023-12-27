'use client';
import { useEffect } from "react";
import Header from "@/components/header";
import Error from "@/components/error";
// import Footer from "@/components/footer";

export default function Home() {
  return (
    <div>
      <Header />
      <Error />
      {/* <Footer/> */}
    </div>
  )
}

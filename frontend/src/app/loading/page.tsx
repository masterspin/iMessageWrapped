'use client';
import { useEffect } from "react";
import Header from "@/components/header";
import Loading from "@/components/loading";
// import Footer from "@/components/footer";

export default function Home() {
  return (
    <div>
      <Header />
      <Loading />
      {/* <Footer/> */}
    </div>
  )
}

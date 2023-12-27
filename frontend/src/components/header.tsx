import React from 'react'
import Link from 'next/link'
import * as ROUTES from "../constants/routes";
import Image from 'next/image'
import "@/app/extra.scss"

type headerProps = {
    
};

const header:React.FC<headerProps> = () => {
    
    return(
        <header className="shadow"  style={{backgroundColor:	"#218aff"}}>
      <div className="relative z-20">
        <div className="px-3 md:px-3 lg:container lg:mx-auto lg:py-4">
          <div className="flex items-center justify-between">
          <div className="flex">
            <Link href="/">
          <Image
            src="/logo.gif"
            width={250}
            height={500}
            alt="iMessage Wrapped"
            />
            </Link>
          </div>
          <div className="typing-indicator items-center">
            <span></span>
            <span></span>
            <span></span>
          </div>

            <div className="flex items-center justify-end">
              <input
                type="checkbox"
                name="hamburger"
                id="hamburger"
                className="peer"
                hidden
              />
              <label
                htmlFor="hamburger"
                className="peer-checked:hamburger block relative z-20 p-6 -mr-6 cursor-pointer lg:hidden"
              >
                <div
                  aria-hidden="true"
                  className="m-auto h-0.5 w-6 rounded bg-sky-900 transition duration-300"
                ></div>
                <div
                  aria-hidden="true"
                  className="m-auto mt-2 h-0.5 w-6 rounded bg-sky-900 transition duration-300"
                ></div>
              </label>

              <div className="peer-checked:translate-x-0 fixed inset-0 w-[calc(100%-4.5rem)] translate-x-[-100%] shadow-xl transition duration-300 lg:border-r-0 lg:w-auto lg:static lg:shadow-none lg:translate-x-0 font-white" style={{backgroundColor:	"#218aff"}}>
                <div className="flex flex-col h-full justify-between lg:items-center lg:flex-row">
                  <ul className="px-6 pt-32 text-gray-700 space-y-8 md:px-12 lg:space-y-0 lg:flex lg:space-x-12 lg:pt-0">
                    <li className="text-white pb-2 group relative before:absolute before:inset-x-0 before:bottom-0 before:h-2 before:origin-right before:scale-x-0 before:bg-white before:transition before:duration-200 hover:before:origin-left hover:before:scale-x-100">
                      <Link className='font-bold text-2xl' href={ROUTES.ABOUT}>About</Link>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
    )
}
export default header;
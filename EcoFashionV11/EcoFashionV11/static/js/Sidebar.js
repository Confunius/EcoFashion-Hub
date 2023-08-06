import React,{useState} from 'react'
import { useLocation } from 'react-router-dom'
import { Link } from 'react-router-dom'
export default function Sidebar() {
    const location = useLocation()
    console.log('loca: ',location)
    const [isMenuOpen, setIsMenuOpen] = useState(false);

  // Function to toggle the menu visibility
  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };


  return (
    <div className={`bg-sidebar w-72 text-nav font-Montserrat Classic Bold mt-24 py-4 flex flex-col ${isMenuOpen ? 'justify-between':'h-72'}`}>
        <Link to='/home'>
        <div className='flex items-center px-4 border-nav'>
        <i class='bx bxs-home text-3xl mr-5 text-black' ></i>
        <div className='text-xl mt-1'> Home</div>
        </div>
        </Link>
        
        <div className={`pr-4 flex items-center ${isMenuOpen ? 'border-l-16':''} border-t-4 pt-1 border-b-4 pb-1 ${!isMenuOpen && 'mt-3 pl-4'} border-nav `}>
        <i class='bx bxs-user text-3xl mr-5 text-black' ></i>
        <div onClick={toggleMenu} className={`text-xl mt-1 cursor-pointer ${isMenuOpen && 'text-background'} `}> Account Management</div>
        <i class={`bx ${isMenuOpen? 'bx-chevron-up':'bx-chevron-down'} mr-auto text-black text-4xl`}></i>
        </div>

        {isMenuOpen && <>
          <Link to='/'>
        <div className='flex items-center border-b-4 pb-3 border-nav px-4'>
        <div className={`${location.pathname == '/'?'text-background':''} text-xl mt-1`}> Edit Admin Profile</div>
        </div>
        </Link>
        
        <Link to='/customer-accounts'>
        <div className='flex items-center border-b-4 pb-3 border-nav px-4'>
        <div className={`${location.pathname == '/customer-accounts'?'text-background':''} text-xl mt-1`}> Customer Accounts </div>
        </div>
        </Link>

        <Link to='/admin-accounts'>
        <div className='flex items-center border-nav px-4'>
        <div className={`${location.pathname == '/admin-accounts'?'text-background':''} text-xl mt-1`}> Admin Accounts</div>
        </div>
        </Link>
        </>}

        <div className={`pl-4 flex items-center px-4 pt-1 border-b-4 pb-1 ${isMenuOpen && 'border-t-4'} border-nav `}>
        <i class='bx bx-transfer text-3xl mr-5 text-black' ></i>
        <div className={`text-xl mt-1 cursor-pointer `}> Transaction Management</div>
        </div>

        <div className={` flex items-center pt-1 px-4 pb-1 border-nav `}>
        <i class='bx bx-male-female text-3xl mr-5 text-black' ></i>
        <div className='text-xl mt-1 cursor-pointer '> Customer Management</div>
        </div>

       
        

    </div>
  )
}

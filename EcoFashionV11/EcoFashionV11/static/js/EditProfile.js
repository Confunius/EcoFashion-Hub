import React, { useState } from 'react'
import AdminFrom from './AdminFrom'
import AdminPasswordForm from './AdminPasswordForm'

export default function EditProfile() {
    const [adminForm,setAdminForm] = useState(true)
  return (
    <div className=' text-white text-lg'>
        <div className='flex items-center mb-6'>
        <div className='font-bold text-2xl'>Edit Admin Profile </div>
        <i className='bx bx-chevron-down text-4xl mt-1 text-white'></i>
        </div>
        <div className='flex items-center'>
        <i className='bx bx-user-circle mr-4 text-4xl text-white'></i>
        <div>
        <div className=''>ECOFASHION HUB ADMIN</div>
        <div>staff_ID ChrisW</div>
        </div>
        </div>
        <div className='font-semibold text-lg flex mt-5 '>
            <div onClick={()=>setAdminForm(true)} className={`flex items-center cursor-pointer ${adminForm?'text-white':'text-gray-400'}`}>
            <p className=''>DETAILS</p><i className='bx bx-chevron-down mr-8 text-4xl '></i>
            </div>
            <div onClick={()=> setAdminForm(false)} className={`flex items-center cursor-pointer ${!adminForm?'text-white':'text-gray-400'}`}>
            <p className=''>PASSWORD</p><i className='bx bx-chevron-down text-4xl '></i>
            </div>
            
        </div>
        {adminForm ? <AdminFrom/>: <AdminPasswordForm/>}
        
    </div>
  )
}

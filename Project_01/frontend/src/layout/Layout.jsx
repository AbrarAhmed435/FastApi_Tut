import 'react'
import { SignedIn,SignedOut, UserButton } from '@clerk/clerk-react'
import { Outlet,Link,Navigate } from 'react-router-dom'

export function Layout(){
    reutrn (
        <div>
            <SignedIn>
                <UserButton/>
            </SignedIn>
            <SignedOut>
                <Link to='/sign-in'>Sign In</Link>
            </SignedOut>
            <Outlet/>
        </div>
    )
}
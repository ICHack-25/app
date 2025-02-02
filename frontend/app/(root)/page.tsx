import { BenefitsSection } from "@/components/layout/sections/benefits";
import { CommunitySection } from "@/components/layout/sections/community";
import { ContactSection } from "@/components/layout/sections/contact";
import { FAQSection } from "@/components/layout/sections/faq";
import { FeaturesSection } from "@/components/layout/sections/features";
import { FooterSection } from "@/components/layout/sections/footer";
import { HeroSection } from "@/components/layout/sections/hero";
import { PricingSection } from "@/components/layout/sections/pricing";
import { ServicesSection } from "@/components/layout/sections/services";
import { SponsorsSection } from "@/components/layout/sections/sponsors";
import { TeamSection } from "@/components/layout/sections/team";
import { TestimonialSection } from "@/components/layout/sections/testimonial";
import {Network} from "@/components/ui/network";
import { ClusterNetwork } from "@/components/ui/clusternetwork";
import { Container } from "@/components/layout/sections/container";
import {InputFile} from "@/components/ui/fileupload";


import { DataObject }  from '../../components/dataobject';
// import {signIn} from "@/app/auth";
import { useSession, signIn, signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";

const dataObjects: DataObject[] = [
    new DataObject('File1', 'txt', '/path/to/file1.txt'),
    new DataObject('File2', 'pdf', '/path/to/file2.pdf'),
    new DataObject('File3', 'jpg', '/path/to/file3.jpg'),
    new DataObject('File4', 'docx', '/path/to/file4.docx')
];

const plainData = dataObjects.map(obj => obj.toPlainObject());

export const metadata = {
  title: "Shadcn - Landing template",
  description: "Free Shadcn landing page for developers",
  openGraph: {
    type: "website",
    url: "https://github.com/nobruf/shadcn-landing-page.git",
    title: "Shadcn - Landing template",
    description: "Free Shadcn landing page for developers",
    images: [
      {
        url: "https://res.cloudinary.com/dbzv9xfjp/image/upload/v1723499276/og-images/shadcn-vue.jpg",
        width: 1200,
        height: 630,
        alt: "Shadcn - Landing template",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    site: "https://github.com/nobruf/shadcn-landing-page.git",
    title: "Shadcn - Landing template",
    description: "Free Shadcn landing page for developers",
    images: [
      "https://res.cloudinary.com/dbzv9xfjp/image/upload/v1723499276/og-images/shadcn-vue.jpg",
    ],
  },
};

export default function Home()  {
    const { data: session} = useSession();

    return (
    <>
        {!session ? (
            <Button
                className="px-6 text-sm font-medium hover:text-gray-300 transition-colors duration-300"
                onClick={async () => {
                    signIn("google", { callbackUrl: "http://localhost:3000/" });
                }}
            >
                Login
            </Button>
        ) : (
            <Button
                className="px-6 text-sm font-medium hover:text-gray-300 transition-colors duration-300"
                onClick={() => {
                    signOut();
                }}
            >
                Sign Out {/* {session.user?.name} */}
            </Button>
        )}

        {/*{ !session ?  <>*/}
        {/*        <HeroSection />*/}
        {/*        /!* <SponsorsSection /> *!/*/}
        {/*        /!* <BenefitsSection /> *!/*/}
        {/*        /!* <FeaturesSection /> *!/*/}
        {/*        <Container>*/}
        {/*            <InputFile/>*/}
        {/*            <ClusterNetwork data={plainData}/>*/}
        {/*        </Container>*/}

        {/*        <ServicesSection />*/}
        {/*        <TestimonialSection />*/}
        {/*        /!* <TeamSection /> *!/*/}
        {/*        <CommunitySection />*/}
        {/*        <PricingSection />*/}
        {/*        /!* <ContactSection /> *!/*/}
        {/*        <FAQSection />*/}
        {/*        <FooterSection />*/}
        {/*    </>*/}
        {/* :*/}
        {/*    <button onClick={signIn('google')}>*/}
        {/*        <span>Login</span>*/}

        {/*    </button>*/}
        {/*}*/}

    </>
  );
}

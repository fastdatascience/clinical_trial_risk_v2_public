import Button from "@material-tailwind/react/components/Button";

const GoogleAuthButton = ({
    btnText,
    handleGoogleAuth,
}: {
    btnText: string;
    handleGoogleAuth: () => void;
}) => {
    return (
        <Button
            variant="outlined"
            className="flex w-full rounded-full items-center justify-center gap-2"
            onClick={handleGoogleAuth}
        >
            <img
                src="https://docs.material-tailwind.com/icons/google.svg"
                alt="google"
                className="h-4 w-4"
            />
            {btnText}
        </Button>
    );
};

export default GoogleAuthButton;

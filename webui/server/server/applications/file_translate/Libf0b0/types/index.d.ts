/// <reference types="react" />
interface Props {
    save_data: (user_data: any) => void;
    FileUploadConponent: (props: {
        onUploadSuccess: (file_path: string) => void;
        title?: string;
    }) => React.ReactElement;
}
declare const Libf0b0: (props: Props) => import("react/jsx-runtime").JSX.Element;
export default Libf0b0;

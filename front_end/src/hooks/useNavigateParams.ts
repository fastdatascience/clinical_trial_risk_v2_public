import { useNavigate } from "react-router-dom";

export const useNavigateParams = () => {
  const navigate = useNavigate();

  return (url: string, params: { queryParam: string }) => {
    const path = `${url}?${params?.queryParam}`;
    navigate(path);
  };
};

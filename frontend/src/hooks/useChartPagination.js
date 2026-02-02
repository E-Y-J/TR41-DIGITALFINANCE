import { useState, useEffect, useMemo } from "react";

export const useChartPagination = (fullDataset, itemsPerPage = 5) => {
  const [page, setPage] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  const totalPages = Math.ceil(fullDataset.length / itemsPerPage);

  const currentData = useMemo(() => {
    return fullDataset.slice(page * itemsPerPage, (page + 1) * itemsPerPage);
  }, [fullDataset, page, itemsPerPage]);

  useEffect(() => {
    if (isPaused) return;
    const interval = setInterval(() => {
      setPage((prev) => (prev === totalPages - 1 ? 0 : prev + 1));
    }, 5000);
    return () => clearInterval(interval);
  }, [totalPages, isPaused]);

  const handleNext = () => setPage((prev) => (prev + 1) % totalPages);
  const handlePrev = () =>
    setPage((prev) => (prev === 0 ? totalPages - 1 : prev - 1));

  return {
    page,
    totalPages,
    currentData,
    handleNext,
    handlePrev,
    setIsPaused,
  };
};

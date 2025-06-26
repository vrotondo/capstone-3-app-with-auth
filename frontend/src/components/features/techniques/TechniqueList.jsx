import React, { useState } from 'react';
import { Eye, Star, Grid, List, ChevronLeft, ChevronRight } from 'lucide-react';
import TechniqueCard from './TechniqueCard';
import Button from '../../common/Button';

const TechniqueList = ({
    techniques = [],
    loading = false,
    error = null,
    viewMode = 'grid',
    onViewModeChange,
    onTechniqueClick,
    onBookmarkToggle,
    user = null,
    // Pagination props
    currentPage = 1,
    hasMore = false,
    onLoadMore,
    onPageChange,
    // Filter/search props
    totalCount = 0,
    searchQuery = '',
    activeFilters = {}
}) => {
    // Loading skeleton
    const LoadingSkeleton = () => (
        <div className={viewMode === 'grid'
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            : "space-y-4"
        }>
            {Array.from({ length: 6 }, (_, index) => (
                <div key={index} className="bg-white rounded-lg shadow-sm border p-6">
                    <div className="animate-pulse">
                        <div className="flex justify-between items-start mb-4">
                            <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                            <div className="h-5 w-5 bg-gray-200 rounded"></div>
                        </div>
                        <div className="space-y-3">
                            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                            <div className="h-4 bg-gray-200 rounded"></div>
                            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                        </div>
                        <div className="mt-4 flex justify-between">
                            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );

    // Error state
    if (error) {
        return (
            <div className="text-center py-12">
                <div className="text-red-500 text-lg font-medium mb-4">
                    {error}
                </div>
                <Button onClick={() => window.location.reload()}>
                    Try Again
                </Button>
            </div>
        );
    }

    // Empty state
    if (!loading && techniques.length === 0) {
        const hasFilters = searchQuery || Object.keys(activeFilters).some(key => activeFilters[key]);

        return (
            <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                    <Eye className="mx-auto h-12 w-12" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                    {hasFilters ? 'No techniques found' : 'No techniques available'}
                </h3>
                <p className="text-gray-500 mb-6">
                    {hasFilters
                        ? 'Try adjusting your search criteria or filters'
                        : 'Start building your technique library by adding some techniques'
                    }
                </p>
                {hasFilters && (
                    <Button onClick={() => {
                        // Clear filters - this would need to be passed as a prop
                        if (onClearFilters) onClearFilters();
                    }}>
                        Clear Filters
                    </Button>
                )}
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Results Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <h2 className="text-xl font-semibold text-gray-900">
                        {searchQuery ? `Search Results` : 'Techniques'}
                    </h2>
                    <span className="text-sm text-gray-500">
                        {loading ? 'Loading...' : `${techniques.length}${totalCount ? ` of ${totalCount}` : ''} techniques`}
                    </span>
                </div>

                {/* View Mode Toggle */}
                {onViewModeChange && (
                    <div className="flex rounded-lg border border-gray-300">
                        <button
                            onClick={() => onViewModeChange('grid')}
                            className={`px-3 py-2 text-sm rounded-l-lg transition-colors ${viewMode === 'grid'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white text-gray-700 hover:bg-gray-50'
                                }`}
                            title="Grid View"
                        >
                            <Grid className="h-4 w-4" />
                        </button>
                        <button
                            onClick={() => onViewModeChange('list')}
                            className={`px-3 py-2 text-sm rounded-r-lg transition-colors ${viewMode === 'list'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white text-gray-700 hover:bg-gray-50'
                                }`}
                            title="List View"
                        >
                            <List className="h-4 w-4" />
                        </button>
                    </div>
                )}
            </div>

            {/* Search Results Info */}
            {searchQuery && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-800">
                        <strong>Search:</strong> "{searchQuery}"
                        {techniques.length > 0 && (
                            <span className="ml-2">• {techniques.length} results found</span>
                        )}
                    </p>
                </div>
            )}

            {/* Loading State */}
            {loading && techniques.length === 0 ? (
                <LoadingSkeleton />
            ) : (
                <>
                    {/* Techniques Grid/List */}
                    <div className={viewMode === 'grid'
                        ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                        : "space-y-4"
                    }>
                        {techniques.map((technique) => (
                            <TechniqueCard
                                key={technique.id}
                                technique={technique}
                                user={user}
                                viewMode={viewMode}
                                onToggleBookmark={onBookmarkToggle}
                                onViewDetails={onTechniqueClick}
                                isBookmarked={technique.is_bookmarked}
                            />
                        ))}
                    </div>

                    {/* Loading More State */}
                    {loading && techniques.length > 0 && (
                        <div className="text-center py-4">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                            <p className="mt-2 text-gray-600">Loading more techniques...</p>
                        </div>
                    )}

                    {/* Pagination */}
                    {(hasMore || currentPage > 1) && (
                        <div className="flex items-center justify-center gap-4">
                            {/* Previous Page */}
                            {onPageChange && currentPage > 1 && (
                                <Button
                                    variant="outline"
                                    onClick={() => onPageChange(currentPage - 1)}
                                    disabled={loading}
                                >
                                    <ChevronLeft className="h-4 w-4 mr-1" />
                                    Previous
                                </Button>
                            )}

                            {/* Page Info */}
                            {onPageChange && (
                                <span className="text-sm text-gray-600">
                                    Page {currentPage}
                                </span>
                            )}

                            {/* Load More or Next Page */}
                            {hasMore && (
                                onLoadMore ? (
                                    <Button
                                        variant="outline"
                                        onClick={onLoadMore}
                                        disabled={loading}
                                    >
                                        {loading ? (
                                            <>
                                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                                                Loading...
                                            </>
                                        ) : (
                                            <>
                                                Load More
                                                <ChevronRight className="h-4 w-4 ml-1" />
                                            </>
                                        )}
                                    </Button>
                                ) : onPageChange && (
                                    <Button
                                        variant="outline"
                                        onClick={() => onPageChange(currentPage + 1)}
                                        disabled={loading}
                                    >
                                        Next
                                        <ChevronRight className="h-4 w-4 ml-1" />
                                    </Button>
                                )
                            )}
                        </div>
                    )}

                    {/* End of Results */}
                    {!hasMore && techniques.length > 0 && !loading && (
                        <div className="text-center py-8">
                            <p className="text-gray-500">
                                You've reached the end of the results
                            </p>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default TechniqueList;
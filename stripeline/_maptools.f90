! Update the array of conditioning matrices "m" with new samples from
! a TOD. The "pixidx" array contains the zero-based indexes in the Healpix
! map of the polarization angles in the array "angle". Note that
! "pixidx" must be a *zero-based* array! The routine internally does the
! conversion to Fortran indexing (which is 1-based).
subroutine update_condmatr(numpix, pixidx, angle, m)
    implicit none

    integer(kind=8), intent(in) :: numpix
    integer(kind=4), dimension(:), intent(in) :: pixidx
    real(kind=8), dimension(size(pixidx)), intent(in) :: angle
    real(kind=8), dimension(numpix, 9), intent(inout) :: m

    real(kind=8) :: cos2angle
    real(kind=8) :: sin2angle
    real(kind=8) :: sincos2angle
    integer :: i
    integer(kind=4) :: pixidx1

    do i = 1, size(pixidx)
        ! Python indexing to Fortran indexing
        pixidx1 = pixidx(i) + 1

        cos2angle = cos(2.0 * angle(i))
        sin2angle = sin(2.0 * angle(i))
        sincos2angle = sin2angle * cos2angle

        m(pixidx1, 1) = m(pixidx1, 1) + 1
        m(pixidx1, 2) = m(pixidx1, 2) + cos2angle 
        m(pixidx1, 3) = m(pixidx1, 3) + sin2angle 
        m(pixidx1, 4) = m(pixidx1, 4) + cos2angle 
        m(pixidx1, 5) = m(pixidx1, 5) + cos2angle * cos2angle 
        m(pixidx1, 6) = m(pixidx1, 6) + sincos2angle 
        m(pixidx1, 7) = m(pixidx1, 7) + sin2angle 
        m(pixidx1, 8) = m(pixidx1, 8) + sincos2angle 
        m(pixidx1, 9) = m(pixidx1, 9) + sin2angle * sin2angle 
    end do
end subroutine update_condmatr

subroutine binned_map(signal, pixidx, mappixels, hits)
    implicit none

    real(kind=8), dimension(:), intent(in) :: signal
    integer(kind=8), dimension(size(signal)), intent(in) :: pixidx
    real(kind=8), dimension(:), intent(inout) :: mappixels
    integer(kind=8), dimension(size(mappixels)), intent(inout) :: hits

    integer :: i

    mappixels = 0.0
    hits = 0

    do i = 1, size(signal)
        mappixels(pixidx(i) + 1) = mappixels(pixidx(i) + 1) + signal(i)
        hits(pixidx(i) + 1) = hits(pixidx(i) + 1) + 1
    end do

    do i = 1, size(mappixels)
        if (hits(i) .gt. 0) then
            mappixels(i) = mappixels(i) / hits(i)
        end if
    end do

end subroutine binned_map
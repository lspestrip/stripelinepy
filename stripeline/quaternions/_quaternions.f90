! In this file, quaternions are represented using the form
!
!     q = q[1] i + q[2] j + q[3] k + q[4],
!
! i.e., the scalar is the last coefficient in the 4-element array

subroutine qadd(a, b, output)
  real(kind=8), dimension(:, :), intent(in) :: a
  real(kind=8), dimension(size(a, 1), size(a, 2)), intent(in) :: b
  real(kind=8), dimension(size(a, 1), size(a, 2)), intent(out) :: output

  output = a + b

end subroutine qadd

subroutine qdot(a, b, output)
  real(kind=8), dimension(:, :), intent(in) :: a
  real(kind=8), dimension(size(a, 1), size(a, 2)), intent(in) :: b
  real(kind=8), dimension(size(a, 1)), intent(out) :: output
  integer :: i

  do i = 1, size(a, 1)
     output(i) = dot_product(a(i, 1:4), b(i, 1:4))
  enddo

end subroutine qdot

subroutine qnorm(q, output)
  implicit none

  real(kind=8), dimension(:, :), intent(in) :: q
  real(kind=8), dimension(size(q, 1), size(q, 2)), intent(out) :: output
  real(kind=8) :: curnorm
  integer :: i

  do i = 1, size(q, 1)
     curnorm = sqrt(dot_product(q(i, 1:4), q(i, 1:4)))
     if (curnorm .gt. 0.0) then
        output(i, :) = q(i, :) / curnorm
     else
        output(i, :) = 0.0
     endif
  enddo

end subroutine qnorm

subroutine qmul(a, b, output)
  implicit none

  real(kind=8), dimension(:, :), intent(in) :: a
  real(kind=8), dimension(size(a, 1), size(a, 2)), intent(in) :: b
  real(kind=8), dimension(size(a, 1), size(a, 2)), intent(out) :: output
  integer :: i

  do i = 1, size(a, 1)
     output(i, 1) = a(i, 1) * b(i, 4) + a(i, 4) * b(i, 1) + a(i, 2) * b(i, 3) - a(i, 3) * b(i, 2)
     output(i, 2) = a(i, 2) * b(i, 4) + a(i, 4) * b(i, 2) + a(i, 3) * b(i, 1) - a(i, 1) * b(i, 3)
     output(i, 3) = a(i, 3) * b(i, 4) + a(i, 4) * b(i, 3) + a(i, 1) * b(i, 2) - a(i, 2) * b(i, 1)
     output(i, 4) = a(i, 4) * b(i, 4) - a(i, 1) * b(i, 1) - a(i, 2) * b(i, 2) - a(i, 3) * b(i, 3)
  enddo

end subroutine qmul

subroutine qfromaxisangle(axes, angles, output)
  implicit none

  real(kind=8), dimension(:, :), intent(in) :: axes
  real(kind=8), dimension(size(axes, 1)), intent(in) :: angles
  real(kind=8), dimension(size(axes, 1), 4), intent(out) :: output

  integer :: i
  real(kind=8) :: sinangle
  real(kind=8) :: cosangle

  do i = 1, size(axes, 1)
     sinangle = sin(angles(i) / 2)
     cosangle = cos(angles(i) / 2)
     output(i, 1:3) = sinangle * axes(i, :) / sqrt(dot_product(axes(i, :), axes(i, :)))
     output(i, 4) = cosangle
  enddo
end subroutine qfromaxisangle

subroutine qtoaxisangle(q, axes, angles)
  implicit none

  real(kind=8), dimension(:, :), intent(in) :: q
  real(kind=8), dimension(size(q, 1), 3), intent(out) :: axes
  real(kind=8), dimension(size(q, 1)), intent(out) :: angles

  integer :: idx

  do idx = 1, size(q, 1)
     angles(idx) = 2 * acos(q(idx, 4))
     if (angles(idx) == 0.0) then
        axes(idx, :) = 0.0
     else
        axes(idx, :) = q(idx, 1:3) / sin(angles(idx) / 2.0)
     endif
  end do

end subroutine qtoaxisangle

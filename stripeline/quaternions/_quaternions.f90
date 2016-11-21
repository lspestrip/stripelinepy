! In this file, quaternions are represented using the form
!
!     q = q[1] i + q[2] j + q[3] k + q[4],
!
! i.e., the scalar is the last coefficient in the 4-element array

! Add two arrays of quaternions
subroutine qadd(a, b, output)
  real(kind=8), dimension(:, :), intent(in) :: a
  real(kind=8), dimension(size(a, 1), size(a, 2)), intent(in) :: b
  real(kind=8), dimension(size(a, 1), size(a, 2)), intent(out) :: output

  output = a + b
end subroutine qadd

! Perform the dot product between two arrays of quaternions
subroutine qdot(a, b, output)
  real(kind=8), dimension(:, :), intent(in) :: a
  real(kind=8), dimension(size(a, 1), size(a, 2)), intent(in) :: b
  real(kind=8), dimension(size(a, 1)), intent(out) :: output
  integer :: i

  do i = 1, size(a, 1)
     output(i) = dot_product(a(i, 1:4), b(i, 1:4))
  enddo

end subroutine qdot

! Normalize an array of quaternions so that each of them has norm 1
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

! Multiply two arrays of quaternions
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

! Build a rotation quaternion from a set of angles and rotation axes
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
     output(i, 1:3) = sinangle * axes(i, :)
     output(i, 4) = cosangle
  enddo
end subroutine qfromaxisangle

! Given an array of rotation quaternions, return the angles and axes of each
! rotation
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

! Calculate the inverse of a rotation quaternion
subroutine qinvrot(q, output)
  implicit none
  
  real(kind=8), dimension(:, :), intent(in) :: q
  real(kind=8), dimension(size(q, 1), size(q, 2)), intent(out) :: output

  integer :: idx

  do idx = 1, size(q, 1)
    output(idx, 1:3) = -q(idx, 1:3)
    output(idx, 4) = q(idx, 4)
  enddo
end subroutine qinvrot

! Rotate an array of vectors using the array of rotation quaternions
! The array "buffer" should have the same size as "quat", and it is used
! as an internal memory buffer
subroutine qrotate(vec, quat, output)
  implicit none

  real(kind=8), dimension(:, :), intent(in) :: vec
  real(kind=8), dimension(size(vec, 1), 4), intent(in) :: quat
  real(kind=8), dimension(size(vec, 1), size(vec, 2)), intent(out) :: output

  ! The computation is the following (in symbols):
  !     output = inv(quat) * (vec * quat)
  ! We use "tmpq" to store the value of "vec * quat"
  real(kind=8), dimension(4) :: tmpq
  integer :: i

  do i = 1, size(vec, 1)
     ! This code is like "qmul", but it assumes that "vec" is an array of
     ! 3-element vector instead of an array of 4-element quaternions: so a few
     ! terms can be safely dropped (vec(i, 4) is always zero!)
     tmpq(1) =  vec(i, 1) * quat(i, 4) + vec(i, 2) * quat(i, 3) - vec(i, 3) * quat(i, 2)
     tmpq(2) =  vec(i, 2) * quat(i, 4) + vec(i, 3) * quat(i, 1) - vec(i, 1) * quat(i, 3)
     tmpq(3) =  vec(i, 3) * quat(i, 4) + vec(i, 1) * quat(i, 2) - vec(i, 2) * quat(i, 1)
     tmpq(4) = -vec(i, 1) * quat(i, 1) - vec(i, 2) * quat(i, 2) - vec(i, 3) * quat(i, 3)

     ! This code is again like "qmul", but we drop the last term, as we are
     ! only interested in the "vector" part of the computation (i.e., the first
     ! three elements of the "output(i, :)" quaternion)
     output(i, 1) = -quat(i, 1) * tmpq(4) + quat(i, 4) * tmpq(1) &
        - quat(i, 2) * tmpq(3) + quat(i, 3) * tmpq(2)
     output(i, 2) = -quat(i, 2) * tmpq(4) + quat(i, 4) * tmpq(2) &
        - quat(i, 3) * tmpq(1) + quat(i, 1) * tmpq(3)
     output(i, 3) = -quat(i, 3) * tmpq(4) + quat(i, 4) * tmpq(3) &
        - quat(i, 1) * tmpq(2) + quat(i, 2) * tmpq(1)
  enddo
end subroutine qrotate
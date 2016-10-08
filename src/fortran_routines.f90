subroutine test(a, b)
    real(kind=8), intent(in), dimension(:) :: a
    real(kind=8), intent(out), dimension(:) :: b

    b = a
end subroutine test
